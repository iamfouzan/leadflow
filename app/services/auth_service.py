"""Authentication business logic service."""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.models.user import User, UserType
from app.repositories.user_repository import UserRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.business_repository import BusinessRepository
from app.core.security import hash_password, verify_password, create_access_token, revoke_token, revoke_all_user_tokens
from app.core.exceptions import ValidationException, AuthenticationException, ResourceNotFoundException
from app.schemas.auth import RegisterRequest, LoginRequest
from app.models.customer import Customer
from app.models.business import Business

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for registration, login, and logout."""

    def __init__(self, db: Session):
        """
        Initialize auth service.

        Args:
            db: Database session
        """
        self.db = db
        self.user_repository = UserRepository(db)
        self.customer_repository = CustomerRepository(db)
        self.business_repository = BusinessRepository(db)

    def register(self, register_data: RegisterRequest) -> User:
        """
        Register new user (Customer, Business Owner, or Admin).

        Args:
            register_data: Registration request data

        Returns:
            Created user instance

        Raises:
            ValidationException: If email or phone already exists
        """
        # Check if email already exists
        existing_user = self.user_repository.get_by_email(register_data.email)
        if existing_user:
            raise ValidationException("Email already registered")

        # Check if phone already exists (if provided)
        if register_data.phone:
            existing_phone = self.user_repository.get_by_phone(register_data.phone)
            if existing_phone:
                raise ValidationException("Phone number already registered")

        # Validate: have_subscription only for business owners
        if register_data.user_type != UserType.BUSINESS_OWNER and register_data.have_subscription is not None:
            raise ValidationException("have_subscription field is only valid for business owners")

        # Hash password
        try:
            password_hash = hash_password(register_data.password)
        except ValueError as e:
            raise ValidationException(f"Password validation failed: {str(e)}")

        # Create user
        user_data = {
            "email": register_data.email,
            "password_hash": password_hash,
            "full_name": register_data.full_name,
            "phone": register_data.phone,
            "user_type": register_data.user_type.value,
            "is_verified": False,
            "address": register_data.address,
            "city": register_data.city,
            "state": register_data.state,
            "country": register_data.country,
            "picture": register_data.picture,
            "gender": register_data.gender.value if register_data.gender else None,
        }

        user = self.user_repository.create(user_data)

        # Create profile based on user type
        if register_data.user_type == UserType.CUSTOMER:
            customer_data = {"user_id": user.id}
            self.customer_repository.create(customer_data)
        elif register_data.user_type == UserType.BUSINESS_OWNER:
            business_data = {
                "user_id": user.id,
                "have_subscription": register_data.have_subscription or False,
            }
            self.business_repository.create(business_data)
        # ADMIN users don't need a profile table (they only exist in users table)

        logger.info(f"User registered: {user.email} ({user.user_type})")
        return user

    def login(
        self,
        login_data: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Login user and generate access token.

        Args:
            login_data: Login request data
            ip_address: Client IP address (optional, for security tracking)
            user_agent: Client user agent (optional, for security tracking)

        Returns:
            Dictionary with user and token

        Raises:
            AuthenticationException: If credentials are invalid
        """
        # Get user by email
        user = self.user_repository.get_by_email(login_data.email)
        if not user:
            raise AuthenticationException("Invalid email or password")

        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise AuthenticationException("Invalid email or password")

        # Create access token (stored in database with hash)
        access_token = create_access_token(
            db=self.db,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_hours=24,  # Token valid for 24 hours
        )

        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

        logger.info(f"User logged in: {user.email}")

        return {
            "user": user,
            "access_token": access_token,
            "token_type": "bearer",
        }

    def logout(self, token: str) -> bool:
        """
        Logout user by revoking token.

        Args:
            token: Access token to revoke

        Returns:
            True if logout successful
        """
        revoked = revoke_token(self.db, token)
        logger.info("User logged out")
        return revoked

    def logout_all_devices(self, user_id) -> int:
        """
        Logout user from all devices by revoking all tokens.

        Args:
            user_id: User ID (UUID)

        Returns:
            Number of tokens revoked
        """
        count = revoke_all_user_tokens(self.db, user_id)
        logger.info(f"User logged out from all devices: {count} sessions ended")
        return count

    def reset_password(self, user_id, new_password: str) -> bool:
        """
        Reset user password.

        Args:
            user_id: User ID (UUID)
            new_password: New password

        Returns:
            True if password reset successful

        Raises:
            ResourceNotFoundException: If user not found
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User", str(user_id))

        # Hash new password
        try:
            password_hash = hash_password(new_password)
        except ValueError as e:
            raise ValidationException(f"Password validation failed: {str(e)}")

        # Update password
        user.password_hash = password_hash
        self.db.commit()
        self.db.refresh(user)

        logger.info(f"Password reset for user: {user.email}")
        return True

