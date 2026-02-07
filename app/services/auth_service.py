"""Authentication business logic service."""
from datetime import timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.models.user import User, UserType
from app.repositories.user_repository import UserRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.business_repository import BusinessRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, generate_token_data, blacklist_token
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

    def login(self, login_data: LoginRequest) -> Dict[str, Any]:
        """
        Login user and generate JWT tokens.

        Args:
            login_data: Login request data

        Returns:
            Dictionary with user and tokens

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

        # Generate token data (convert UUID to string)
        token_data = generate_token_data(str(user.id), user.email, user.user_type.value)

        # Create tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

        logger.info(f"User logged in: {user.email}")

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def logout(self, token: str) -> bool:
        """
        Logout user by blacklisting token.

        Args:
            token: JWT access token to blacklist

        Returns:
            True if logout successful
        """
        blacklist_token(token)
        logger.info("User logged out")
        return True

    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: JWT refresh token

        Returns:
            Dictionary with new access token

        Raises:
            AuthenticationException: If refresh token is invalid
        """
        from app.core.security import decode_token

        # Decode refresh token
        payload = decode_token(refresh_token)
        if not payload:
            raise AuthenticationException("Invalid refresh token")

        # Check token type
        if payload.get("type") != "refresh":
            raise AuthenticationException("Invalid token type")

        # Get user
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationException("Invalid token payload")

        from uuid import UUID
        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError):
            raise AuthenticationException("Invalid user ID in token")

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise AuthenticationException("User not found")

        # Generate new access token (convert UUID to string)
        token_data = generate_token_data(str(user.id), user.email, user.user_type.value)
        access_token = create_access_token(token_data)

        logger.info(f"Access token refreshed for user: {user.email}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

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

