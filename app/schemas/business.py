"""Business schemas."""
from app.schemas.user import UserBase, UserResponse
from pydantic import BaseModel


class BusinessBase(UserBase):
    """Base business schema."""

    pass


class BusinessCreate(BusinessBase):
    """Business creation schema."""

    password: str
    email: str


class BusinessResponse(UserResponse):
    """Business response schema."""

    pass

