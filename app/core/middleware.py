"""Custom middleware (logging, timing, rate limiting)."""
import time
import logging
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from redis import Redis

from app.config import settings

logger = logging.getLogger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request processing time."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log timing."""
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        response.headers["X-Process-Time"] = str(process_time)
        logger.info(
            f"Request processed: {request.method} {request.url.path} - "
            f"{response.status_code} - {process_time:.3f}s"
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting per IP and per user."""

    def __init__(self, app: ASGIApp):
        """Initialize rate limiting middleware."""
        super().__init__(app)
        self.rate_limit = settings.RATE_LIMIT_PER_MINUTE

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        # Get Redis client from app state
        redis_client = getattr(request.app.state, "redis_client", None)

        # Skip rate limiting if Redis is not available
        if not redis_client:
            response = await call_next(request)
            return response

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Create rate limit key
        rate_limit_key = f"rate_limit:{client_ip}"

        try:
            # Check current count
            current_count = redis_client.get(rate_limit_key)
            if current_count is None:
                current_count = 0
            else:
                current_count = int(current_count)

            # Check if rate limit exceeded
            if current_count >= self.rate_limit:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return Response(
                    content='{"detail": "Rate limit exceeded"}',
                    status_code=429,
                    headers={"Content-Type": "application/json"},
                )

            # Increment count
            redis_client.incr(rate_limit_key)
            redis_client.expire(rate_limit_key, 60)  # 1 minute window
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # Continue processing if rate limiting fails

        # Process request
        response = await call_next(request)
        return response

