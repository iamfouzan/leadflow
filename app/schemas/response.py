"""Standard response schemas."""
from typing import Generic, TypeVar, List, Optional, Dict, Any
from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response wrapper."""

    success: bool = True
    data: T
    message: Optional[str] = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""

    success: bool = False
    error: Dict[str, Any]

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    success: bool = True
    data: List[T]
    pagination: Dict[str, Any]

    class Config:
        """Pydantic configuration."""

        from_attributes = True

