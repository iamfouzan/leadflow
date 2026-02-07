"""Business data access repository."""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.business import Business


class BusinessRepository(BaseRepository[Business]):
    """Business repository."""

    def __init__(self, db: Session):
        """Initialize business repository."""
        super().__init__(Business, db)

    def get_by_user_id(self, user_id: UUID) -> Optional[Business]:
        """
        Get business by user ID.

        Args:
            user_id: User ID (UUID)

        Returns:
            Business instance or None if not found
        """
        return self.db.query(Business).filter(Business.user_id == user_id).first()

