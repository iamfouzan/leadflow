"""Authentication REST API endpoints."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from redis import Redis

from app.api.deps import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    OTPRequest,
    OTPVerifyRequest,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.schemas.response import SuccessResponse, ErrorResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.otp_service import OTPService
from app.repositories.user_repository import UserRepository
from app.core.exceptions import (
    ValidationException,
    AuthenticationException,
    ResourceNotFoundException,
    OTPException,
)
from app.config import settings

router = APIRouter()

# Global Redis client (will be injected)
redis_client: Redis = None


def get_redis_client() -> Redis:
    """Get Redis client."""
    global redis_client
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client


@router.post(
    "/register",
    response_model=SuccessResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db),
) -> SuccessResponse[UserResponse]:
    """
    Register new user (Customer or Business Owner).

    Args:
        register_data: Registration request data
        db: Database session

    Returns:
        Success response with created user data
    """
    auth_service = AuthService(db)
    try:
        user = auth_service.register(register_data)
        return SuccessResponse(
            data=UserResponse.model_validate(user),
            message="User registered successfully. Please verify your email.",
        )
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/send-otp",
    response_model=SuccessResponse[dict],
    status_code=status.HTTP_200_OK,
)
async def send_otp(
    otp_request: OTPRequest,
    db: Session = Depends(get_db),
) -> SuccessResponse[dict]:
    """
    Send OTP to email for verification.

    Args:
        otp_request: OTP request data
        db: Database session

    Returns:
        Success response
    """
    redis_client = get_redis_client()
    otp_service = OTPService(redis_client)
    user_repository = UserRepository(db)

    # Get user by email
    user = user_repository.get_by_email(otp_request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        otp_service.create_and_send_otp(user.id, user.email, purpose="verification")
        return SuccessResponse(
            data={},
            message=f"OTP sent to {otp_request.email}",
        )
    except OTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/verify-otp",
    response_model=SuccessResponse[UserResponse],
    status_code=status.HTTP_200_OK,
)
async def verify_otp(
    verify_request: OTPVerifyRequest,
    db: Session = Depends(get_db),
) -> SuccessResponse[UserResponse]:
    """
    Verify OTP and activate account.

    Args:
        verify_request: OTP verification request data
        db: Database session

    Returns:
        Success response with activated user data
    """
    redis_client = get_redis_client()
    otp_service = OTPService(redis_client)
    user_repository = UserRepository(db)

    # Get user by email
    user = user_repository.get_by_email(verify_request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        # Verify OTP
        otp_service.verify_otp(user.id, verify_request.otp)

        # Activate user
        user_repository.verify_user(user.id)

        return SuccessResponse(
            data=UserResponse.model_validate(user),
            message="Email verified successfully. Your account is now active.",
        )
    except OTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> SuccessResponse[TokenResponse]:
    """
    Login with email and password.

    Args:
        login_data: Login request data
        request: FastAPI request object (for IP and user agent tracking)
        db: Database session

    Returns:
        Success response with access token
    """
    auth_service = AuthService(db)
    try:
        # Extract IP and user agent for security tracking
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        result = auth_service.login(
            login_data=login_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return SuccessResponse(
            data=TokenResponse(
                access_token=result["access_token"],
                token_type=result["token_type"],
            ),
            message="Login successful",
        )
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/forgot-password",
    response_model=SuccessResponse[dict],
    status_code=status.HTTP_200_OK,
)
async def forgot_password(
    forgot_request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> SuccessResponse[dict]:
    """
    Request password reset OTP.

    Args:
        forgot_request: Forgot password request data
        db: Database session

    Returns:
        Success response
    """
    redis_client = get_redis_client()
    otp_service = OTPService(redis_client)
    user_repository = UserRepository(db)

    # Get user by email
    user = user_repository.get_by_email(forgot_request.email)
    if not user:
        # Don't reveal if user exists or not
        return SuccessResponse(
            data={},
            message="If the email exists, an OTP has been sent.",
        )

    try:
        otp_service.create_and_send_otp(user.id, user.email, purpose="password_reset")
        return SuccessResponse(
            data={},
            message="If the email exists, an OTP has been sent.",
        )
    except OTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/reset-password",
    response_model=SuccessResponse[dict],
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    reset_request: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> SuccessResponse[dict]:
    """
    Reset password with OTP verification.

    Args:
        reset_request: Reset password request data
        db: Database session

    Returns:
        Success response
    """
    redis_client = get_redis_client()
    otp_service = OTPService(redis_client)
    user_repository = UserRepository(db)
    auth_service = AuthService(db)

    # Get user by email
    user = user_repository.get_by_email(reset_request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        # Verify OTP
        otp_service.verify_otp(user.id, reset_request.otp)

        # Reset password
        auth_service.reset_password(user.id, reset_request.new_password)

        return SuccessResponse(
            data={},
            message="Password reset successfully",
        )
    except OTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/logout",
    response_model=SuccessResponse[dict],
    status_code=status.HTTP_200_OK,
)
async def logout(
    request: Request,
    db: Session = Depends(get_db),
) -> SuccessResponse[dict]:
    """
    Logout user by blacklisting token.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        Success response
    """
    auth_service = AuthService(db)

    # Extract token from Authorization header
    authorization: str = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    token = authorization.replace("Bearer ", "")
    auth_service.logout(token)

    return SuccessResponse(
        data={},
        message="Logged out successfully",
    )

