"""OTP storage model."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import BaseModel


class OTP(BaseModel):
    """OTP model for storing verification codes."""

    __tablename__ = "otps"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_used = Column(Boolean, default=False, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_otps_user_id", "user_id"),
        Index("idx_otps_expires_at", "expires_at"),
        Index("idx_otps_is_used", "is_used"),
    )

    def __repr__(self) -> str:
        """String representation of OTP."""
        return f"<OTP id={self.id} user_id={self.user_id} is_used={self.is_used}>"

