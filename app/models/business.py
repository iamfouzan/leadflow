"""Business model."""
from sqlalchemy import Column, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class Business(BaseModel):
    """Business model - extends User."""

    __tablename__ = "businesses"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    have_subscription = Column(Boolean, default=False, nullable=False)

    # Relationship
    user = relationship("User", back_populates="business_profile")

    def __repr__(self) -> str:
        """String representation of Business."""
        return f"<Business id={self.id} user_id={self.user_id} have_subscription={self.have_subscription}>"

