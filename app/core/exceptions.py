"""Custom exception classes."""
from typing import Any


class AppException(Exception):
    """Base exception for application."""

    def __init__(self, message: str):
        """Initialize exception with message."""
        self.message = message
        super().__init__(self.message)


class ResourceNotFoundException(AppException):
    """Raised when resource is not found."""

    def __init__(self, resource: str, id: Any):
        """Initialize exception with resource name and ID."""
        self.resource = resource
        self.id = id
        self.message = f"{resource} with id {id} not found"
        super().__init__(self.message)


class UnauthorizedException(AppException):
    """Raised when user is not authorized."""

    def __init__(self, message: str = "Not authorized"):
        """Initialize exception with message."""
        super().__init__(message)


class ValidationException(AppException):
    """Raised when validation fails."""

    def __init__(self, message: str = "Validation failed"):
        """Initialize exception with message."""
        super().__init__(message)


class AuthenticationException(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        """Initialize exception with message."""
        super().__init__(message)


class OTPException(AppException):
    """Raised when OTP operation fails."""

    def __init__(self, message: str = "OTP operation failed"):
        """Initialize exception with message."""
        super().__init__(message)

