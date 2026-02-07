"""Access token model for simple token authentication."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import BaseModel


class AccessToken(BaseModel):
    """Access token model for authentication."""

    __tablename__ = "access_tokens"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA256 hash
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(512), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Relationship
    user = relationship("User", backref="access_tokens")

    # Indexes for performance
    __table_args__ = (
        Index("idx_access_tokens_token_hash", "token_hash"),
        Index("idx_access_tokens_user_id", "user_id"),
        Index("idx_access_tokens_expires_at", "expires_at"),
    )

    def __repr__(self) -> str:
        """String representation of AccessToken."""
        return f"<AccessToken id={self.id} user_id={self.user_id} expires_at={self.expires_at}>"
