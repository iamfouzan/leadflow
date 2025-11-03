"""User base model."""
import enum
from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import BaseModel


class UserType(str, enum.Enum):
    """User type enumeration."""

    CUSTOMER = "CUSTOMER"
    BUSINESS_OWNER = "BUSINESS_OWNER"


class UserStatus(str, enum.Enum):
    """User status enumeration."""

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class User(BaseModel):
    """User model - base table for all users."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    user_type = Column(Enum(UserType), nullable=False, index=True)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer_profile = relationship("Customer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    business_profile = relationship("Business", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_phone", "phone"),
        Index("idx_users_user_type", "user_type"),
        Index("idx_users_status", "status"),
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User id={self.id} email={self.email} user_type={self.user_type}>"

