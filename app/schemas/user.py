"""User schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserType, UserStatus


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)
    user_type: UserType


class UserUpdate(BaseModel):
    """User update schema."""

    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UserResponse(UserBase):
    """User response schema."""

    id: int
    user_type: UserType
    status: UserStatus
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True

