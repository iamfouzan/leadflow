"""FastAPI application entry point."""
import logging
import sys
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis import Redis

from app.config import settings
from app.core.exceptions import (
    AppException,
    ResourceNotFoundException,
    UnauthorizedException,
    ValidationException,
    AuthenticationException,
    OTPException,
)
from app.core.middleware import TimingMiddleware, RateLimitMiddleware
from app.core.security import set_redis_client
from app.api.v1.router import api_router
from app.db.session import SessionLocal, engine
from app.db.base import Base

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Global Redis client
redis_client: Optional[Redis] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting application...")

    # Initialize Redis connection
    global redis_client
    try:
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()
        set_redis_client(redis_client)
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        if settings.is_production:
            raise
        # In local, continue without Redis for development

    # Store Redis client in app state for middleware access
    app.state.redis_client = redis_client

    # Set Redis client in auth endpoints module
    import app.api.v1.endpoints.auth as auth_module
    auth_module.redis_client = redis_client

    # Create database tables (only in development)
    if settings.is_local:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created (local environment)")

    logger.info("Application started successfully")
    yield

    # Shutdown
    logger.info("Shutting down application...")

    # Close Redis connection
    if redis_client:
        redis_client.close()
        logger.info("Redis connection closed")

    # Close database connections
    SessionLocal.close_all()
    logger.info("Database connections closed")

    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="LeadFlow Backend API",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(TimingMiddleware)

# Add rate limiting middleware (Redis will be stored in app.state during startup)
from app.core.middleware import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Exception handlers
@app.exception_handler(ResourceNotFoundException)
async def resource_not_found_handler(
    request: Request, exc: ResourceNotFoundException
) -> JSONResponse:
    """Handle resource not found exceptions."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": exc.message if settings.is_local else "Resource not found",
            },
        },
    )


@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(
    request: Request, exc: UnauthorizedException
) -> JSONResponse:
    """Handle unauthorized exceptions."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": exc.message if settings.is_local else "Unauthorized",
            },
        },
    )


@app.exception_handler(ValidationException)
async def validation_handler(
    request: Request, exc: ValidationException
) -> JSONResponse:
    """Handle validation exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": exc.message if settings.is_local else "Validation failed",
            },
        },
    )


@app.exception_handler(AuthenticationException)
async def authentication_handler(
    request: Request, exc: AuthenticationException
) -> JSONResponse:
    """Handle authentication exceptions."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "error": {
                "code": "AUTHENTICATION_ERROR",
                "message": exc.message if settings.is_local else "Authentication failed",
            },
        },
    )


@app.exception_handler(OTPException)
async def otp_handler(request: Request, exc: OTPException) -> JSONResponse:
    """Handle OTP exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "code": "OTP_ERROR",
                "message": exc.message if settings.is_local else "OTP operation failed",
            },
        },
    )


@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request, exc: AppException
) -> JSONResponse:
    """Handle general application exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": exc.message if settings.is_local else "An error occurred",
            },
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": (
                    str(exc) if settings.is_local else "An internal error occurred"
                ),
            },
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        Health status dictionary
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root() -> dict:
    """
    Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": "Welcome to Service Marketplace API",
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
    }

