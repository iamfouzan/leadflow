"""Customer schemas."""
from app.schemas.user import UserBase, UserResponse
from pydantic import BaseModel
from datetime import datetime


class CustomerBase(UserBase):
    """Base customer schema."""

    pass


class CustomerCreate(CustomerBase):
    """Customer creation schema."""

    password: str
    email: str


class CustomerResponse(UserResponse):
    """Customer response schema."""

    pass

