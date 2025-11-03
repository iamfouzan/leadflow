"""User data access repository."""
from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.user import User, UserType, UserStatus


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

    def update_status(self, user_id: int, status: UserStatus) -> Optional[User]:
        """
        Update user status.

        Args:
            user_id: User ID
            status: New status

        Returns:
            Updated user instance or None if not found
        """
        user = self.get_by_id(user_id)
        if user:
            user.status = status
            self.db.commit()
            self.db.refresh(user)
        return user

    def verify_user(self, user_id: int) -> Optional[User]:
        """
        Verify user account.

        Args:
            user_id: User ID

        Returns:
            Updated user instance or None if not found
        """
        user = self.get_by_id(user_id)
        if user:
            user.is_verified = True
            user.status = UserStatus.ACTIVE
            self.db.commit()
            self.db.refresh(user)
        return user

