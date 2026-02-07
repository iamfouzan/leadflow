"""Refresh token model."""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import BaseModel


class RefreshToken(BaseModel):
    """Refresh token model for token management."""

    __tablename__ = "refresh_tokens"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(512), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_refresh_tokens_user_id", "user_id"),
        Index("idx_refresh_tokens_expires_at", "expires_at"),
        Index("idx_refresh_tokens_token", "token"),
        Index("idx_refresh_tokens_is_revoked", "is_revoked"),
    )

    def __repr__(self) -> str:
        """String representation of RefreshToken."""
        return f"<RefreshToken id={self.id} user_id={self.user_id} is_revoked={self.is_revoked}>"

