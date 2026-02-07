"""Dependency injection functions."""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db as get_database_session
from app.core.security import validate_token
from app.core.exceptions import UnauthorizedException, AuthenticationException
from app.models.user import User

# HTTP Bearer scheme for simple token authentication
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.

    Yields:
        Session: Database session
    """
    yield from get_database_session()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    request: Request = None,
) -> User:
    """
    Dependency to get current authenticated user via simple token.

    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        request: FastAPI request object (optional, for IP tracking)

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Optional: Extract IP and user agent for security validation
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    # Validate token and get user
    user = validate_token(
        db=db,
        token=token,
        check_ip=ip_address,
        check_user_agent=user_agent,
    )

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_customer(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get current active customer user.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current customer user

    Raises:
        HTTPException: If user is not a customer
    """
    if current_user.user_type != "CUSTOMER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Customer access required.",
        )
    return current_user


async def get_current_active_business(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get current active business owner user.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current business owner user

    Raises:
        HTTPException: If user is not a business owner
    """
    if current_user.user_type != "BUSINESS_OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Business owner access required.",
        )
    return current_user

