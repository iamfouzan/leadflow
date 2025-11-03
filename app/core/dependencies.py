"""Dependency injection functions."""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db as get_database_session
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, AuthenticationException
from app.models.user import User
from app.repositories.user_repository import UserRepository

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.

    Yields:
        Session: Database session
    """
    yield from get_database_session()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get current authenticated user.

    Args:
        token: JWT access token
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user_repository = UserRepository(db)
    user = user_repository.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )

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

