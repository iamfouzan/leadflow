"""User data access repository."""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.user import User, UserType


class UserRepository(BaseRepository[User]):
    """User repository with email lookup methods."""

    def __init__(self, db: Session):
        """Initialize user repository."""
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_by_phone(self, phone: str) -> Optional[User]:
        """
        Get user by phone.

        Args:
            phone: User phone number

        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.phone == phone).first()

    def get_by_email_and_type(self, email: str, user_type: UserType) -> Optional[User]:
        """
        Get user by email and user type.

        Args:
            email: User email
            user_type: User type

        Returns:
            User instance or None if not found
        """
        return (
            self.db.query(User)
            .filter(User.email == email, User.user_type == user_type)
            .first()
        )

    def verify_user(self, user_id: UUID) -> Optional[User]:
        """
        Verify user account via OTP.

        Args:
            user_id: User ID (UUID)

        Returns:
            Updated user instance or None if not found
        """
        user = self.get_by_id(user_id)
        if user:
            user.is_verified = True
            self.db.commit()
            self.db.refresh(user)
        return user

