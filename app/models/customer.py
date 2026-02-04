"""Customer model."""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class Customer(BaseModel):
    """Customer model - extends User."""

    __tablename__ = "customers"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Relationship
    user = relationship("User", back_populates="customer_profile")

    def __repr__(self) -> str:
        """String representation of Customer."""
        return f"<Customer id={self.id} user_id={self.user_id}>"

