"""User schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserType, Gender


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    picture: Optional[str] = None
    gender: Optional[Gender] = None

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
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    picture: Optional[str] = Field(None, max_length=500)
    gender: Optional[Gender] = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UserResponse(UserBase):
    """User response schema."""

    id: UUID
    user_type: UserType
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True

