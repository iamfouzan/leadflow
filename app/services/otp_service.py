"""OTP generation and validation service."""
import secrets
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from redis import Redis
import logging

from app.config import settings
from app.db.session import get_db
from app.repositories.otp_repository import OTPRepository
from app.repositories.user_repository import UserRepository
from app.core.exceptions import OTPException, ValidationException
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class OTPService:
    """OTP service for generation, validation, and cleanup."""

    def __init__(self, redis_client: Redis):
        """
        Initialize OTP service.

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
        self.otp_length = settings.OTP_LENGTH
        self.expiry_minutes = settings.OTP_EXPIRY_MINUTES
        self.max_attempts = settings.OTP_MAX_ATTEMPTS

    def generate_otp(self) -> str:
        """
        Generate cryptographically secure OTP code.

        Returns:
            6-digit OTP code string
        """
        # Generate random digits
        otp = "".join([str(secrets.randbelow(10)) for _ in range(self.otp_length)])
        return otp

    def create_and_send_otp(self, user_id: int, email: str, purpose: str = "verification") -> str:
        """
        Create OTP and send via email.

        Args:
            user_id: User ID
            email: User email address
            purpose: OTP purpose (verification or password_reset)

        Returns:
            Generated OTP code

        Raises:
            OTPException: If OTP creation fails
        """
        # Generate OTP
        otp_code = self.generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=self.expiry_minutes)

        # Store in Redis (primary storage)
        redis_key = f"otp:{user_id}"
        otp_data = {
            "code": otp_code,
            "attempts": 0,
            "created_at": datetime.utcnow().isoformat(),
            "purpose": purpose,
        }
        self.redis.setex(
            redis_key,
            self.expiry_minutes * 60,  # TTL in seconds
            json.dumps(otp_data),
        )

        # Store in PostgreSQL (backup/audit trail)
        db = next(get_db())
        try:
            otp_repository = OTPRepository(db)
            from app.models.otp import OTP

            otp = OTP(
                user_id=user_id,
                code=otp_code,
                expires_at=expires_at,
                is_used=False,
                attempts=0,
            )
            db.add(otp)
            db.commit()
            db.refresh(otp)
        except Exception as e:
            logger.error(f"Failed to store OTP in database: {str(e)}")
            # Continue even if database storage fails - Redis is primary
        finally:
            db.close()

        # Send email
        try:
            if purpose == "password_reset":
                email_service.send_password_reset_email(email, otp_code)
            else:
                email_service.send_otp_email(email, otp_code)
        except Exception as e:
            logger.error(f"Failed to send OTP email: {str(e)}")
            raise OTPException(f"Failed to send OTP email: {str(e)}")

        logger.info(f"OTP created and sent for user {user_id}")
        return otp_code

    def verify_otp(self, user_id: int, otp_code: str) -> bool:
        """
        Verify OTP code.

        Args:
            user_id: User ID
            otp_code: OTP code to verify

        Returns:
            True if OTP is valid, False otherwise

        Raises:
            OTPException: If OTP is invalid, expired, or max attempts exceeded
        """
        redis_key = f"otp:{user_id}"

        # Get from Redis
        otp_data_str = self.redis.get(redis_key)
        if not otp_data_str:
            raise OTPException("OTP expired or not found")

        otp_data = json.loads(otp_data_str)

        # Check attempts
        if otp_data.get("attempts", 0) >= self.max_attempts:
            self.redis.delete(redis_key)
            raise OTPException("Maximum OTP attempts exceeded")

        # Verify code
        if otp_data.get("code") != otp_code:
            # Increment attempts
            otp_data["attempts"] += 1
            self.redis.setex(
                redis_key,
                self.expiry_minutes * 60,
                json.dumps(otp_data),
            )

            # Update attempts in database
            db = next(get_db())
            try:
                otp_repository = OTPRepository(db)
                active_otp = otp_repository.get_active_by_user(user_id)
                if active_otp and active_otp.code == otp_code:
                    otp_repository.increment_attempts(active_otp.id)
            except Exception as e:
                logger.error(f"Failed to update OTP attempts in database: {str(e)}")
            finally:
                db.close()

            raise OTPException("Invalid OTP code")

        # Mark as used in database
        db = next(get_db())
        try:
            otp_repository = OTPRepository(db)
            active_otp = otp_repository.get_active_by_user(user_id)
            if active_otp:
                otp_repository.mark_as_used(active_otp.id)
        except Exception as e:
            logger.error(f"Failed to mark OTP as used in database: {str(e)}")
        finally:
            db.close()

        # Delete from Redis
        self.redis.delete(redis_key)

        logger.info(f"OTP verified successfully for user {user_id}")
        return True

    def cleanup_expired_otps(self) -> int:
        """
        Clean up expired OTPs from database.

        Returns:
            Number of cleaned up OTPs
        """
        db = next(get_db())
        try:
            otp_repository = OTPRepository(db)
            count = otp_repository.cleanup_expired()
            logger.info(f"Cleaned up {count} expired OTPs")
            return count
        finally:
            db.close()

