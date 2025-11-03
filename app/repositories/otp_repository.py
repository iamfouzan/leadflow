"""OTP data access repository."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.repositories.base import BaseRepository
from app.models.otp import OTP


class OTPRepository(BaseRepository[OTP]):
    """OTP repository with validation methods."""

    def __init__(self, db: Session):
        """Initialize OTP repository."""
        super().__init__(OTP, db)

    def get_by_user_and_code(self, user_id: int, code: str) -> Optional[OTP]:
        """
        Get OTP by user ID and code.

        Args:
            user_id: User ID
            code: OTP code

        Returns:
            OTP instance or None if not found
        """
        return (
            self.db.query(OTP)
            .filter(
                and_(
                    OTP.user_id == user_id,
                    OTP.code == code,
                    OTP.is_used == False,
                    OTP.expires_at > datetime.utcnow(),
                )
            )
            .first()
        )

    def get_active_by_user(self, user_id: int) -> Optional[OTP]:
        """
        Get active OTP for user.

        Args:
            user_id: User ID

        Returns:
            Active OTP instance or None if not found
        """
        return (
            self.db.query(OTP)
            .filter(
                and_(
                    OTP.user_id == user_id,
                    OTP.is_used == False,
                    OTP.expires_at > datetime.utcnow(),
                )
            )
            .order_by(OTP.created_at.desc())
            .first()
        )

    def increment_attempts(self, otp_id: int) -> Optional[OTP]:
        """
        Increment OTP attempt count.

        Args:
            otp_id: OTP ID

        Returns:
            Updated OTP instance or None if not found
        """
        otp = self.get_by_id(otp_id)
        if otp:
            otp.attempts += 1
            self.db.commit()
            self.db.refresh(otp)
        return otp

    def mark_as_used(self, otp_id: int) -> Optional[OTP]:
        """
        Mark OTP as used.

        Args:
            otp_id: OTP ID

        Returns:
            Updated OTP instance or None if not found
        """
        otp = self.get_by_id(otp_id)
        if otp:
            otp.is_used = True
            otp.used_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(otp)
        return otp

    def get_expired(self) -> List[OTP]:
        """
        Get all expired unused OTPs.

        Returns:
            List of expired OTP instances
        """
        return (
            self.db.query(OTP)
            .filter(
                and_(
                    OTP.is_used == False,
                    OTP.expires_at < datetime.utcnow(),
                )
            )
            .all()
        )

    def cleanup_expired(self) -> int:
        """
        Clean up expired unused OTPs.

        Returns:
            Number of deleted OTPs
        """
        expired_otps = self.get_expired()
        count = len(expired_otps)
        for otp in expired_otps:
            self.db.delete(otp)
        self.db.commit()
        return count

