"""Authentication schemas."""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserType, Gender


class RegisterRequest(BaseModel):
    """User registration request schema."""

    # Required fields
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Password must be between 8 and 72 characters (bcrypt limit is 72 bytes)",
    )
    full_name: str = Field(..., min_length=1, max_length=100)
    user_type: UserType
    
    # Optional personal information fields
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    picture: Optional[str] = Field(None, max_length=500, description="URL to profile picture")
    gender: Optional[Gender] = None
    
    # Business owner specific field
    have_subscription: Optional[bool] = Field(None, description="Only valid for business owners")


class LoginRequest(BaseModel):
    """User login request schema."""

    email: EmailStr
    password: str


class OTPRequest(BaseModel):
    """OTP request schema."""

    email: EmailStr


class OTPVerifyRequest(BaseModel):
    """OTP verification request schema."""

    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request schema."""

    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="New password must be between 8 and 72 characters (bcrypt limit is 72 bytes)",
    )

