"""Business model."""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class Business(BaseModel):
    """Business model - extends User."""

    __tablename__ = "businesses"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Relationship
    user = relationship("User", back_populates="business_profile")

    def __repr__(self) -> str:
        """String representation of Business."""
        return f"<Business id={self.id} user_id={self.user_id}>"

