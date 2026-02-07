"""Token schemas."""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TokenData(BaseModel):
    """Token data schema."""

    user_id: Optional[UUID] = None
    email: Optional[str] = None
    user_type: Optional[str] = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True

