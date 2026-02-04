"""Customer data access repository."""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.customer import Customer


class CustomerRepository(BaseRepository[Customer]):
    """Customer repository."""

    def __init__(self, db: Session):
        """Initialize customer repository."""
        super().__init__(Customer, db)

    def get_by_user_id(self, user_id: UUID) -> Optional[Customer]:
        """
        Get customer by user ID.

        Args:
            user_id: User ID (UUID)

        Returns:
            Customer instance or None if not found
        """
        return self.db.query(Customer).filter(Customer.user_id == user_id).first()

