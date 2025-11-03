"""JWT, password hashing, and token management."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import bcrypt
from redis import Redis
import secrets
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Password hashing context with explicit bcrypt configuration
# Configure to use bcrypt with default rounds and avoid initialization issues
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Default bcrypt rounds
)

# Use bcrypt directly to avoid passlib initialization issues with bug detection
# Passlib has compatibility issues with bcrypt 5.0.0 during bug detection
# We'll use bcrypt library directly for hashing, passlib can still be used for verification
USE_DIRECT_BCRYPT = True  # Set to True to bypass passlib's bug detection issues

# Redis client (will be initialized in main.py)
redis_client: Optional[Redis] = None


def set_redis_client(client: Redis) -> None:
    """Set Redis client for token blacklisting."""
    global redis_client
    redis_client = client


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string

    Raises:
        ValueError: If password exceeds 72 bytes (bcrypt limit) or other hashing error
    """
    # Bcrypt has a 72-byte limit for passwords
    # Convert to bytes to check length first
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        raise ValueError(
            f"Password cannot exceed 72 bytes. Current length: {len(password_bytes)} bytes"
        )
    
    # Hash password - use bcrypt directly to avoid passlib's bug detection issues
    # Passlib has compatibility issues with bcrypt 5.0.0 during initialization
    try:
        if USE_DIRECT_BCRYPT:
            # Use bcrypt library directly - more reliable with bcrypt 5.0.0
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt(rounds=12)
            hash_bytes = bcrypt.hashpw(password_bytes, salt)
            # Return as string (passlib format expects string)
            return hash_bytes.decode('utf-8')
        else:
            # Fallback to passlib (may fail with bug detection issues)
            return pwd_context.hash(password)
    except ValueError as e:
        error_msg = str(e).lower()
        if "password cannot be longer than 72 bytes" in error_msg:
            # This shouldn't happen since we validated, but handle it
            logger.error(
                f"Password length validation issue: password is {len(password_bytes)} bytes. "
                f"Error: {str(e)}"
            )
            raise ValueError(
                f"Password is too long. Maximum length is 72 bytes ({len(password_bytes)} bytes provided)."
            ) from e
        # Other ValueError
        logger.error(f"Bcrypt ValueError during password hashing: {str(e)}", exc_info=True)
        raise ValueError(
            "Password hashing failed. Please try again with a different password."
        ) from e
    except Exception as e:
        # Other unexpected errors
        logger.error(f"Unexpected error during password hashing: {str(e)}", exc_info=True)
        raise ValueError(
            "Password hashing failed. Please try again or contact support if the issue persists."
        ) from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    try:
        if USE_DIRECT_BCRYPT:
            # Use bcrypt library directly for verification
            password_bytes = plain_password.encode('utf-8')
            hash_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        else:
            # Use passlib for verification
            return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}", exc_info=True)
        # On error, return False (password doesn't match)
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Token payload data
        expires_delta: Optional expiry time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Generate unique token ID
    jti = secrets.token_urlsafe(32)

    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": jti,
        }
    )

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create JWT refresh token.

    Args:
        data: Token payload data

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    # Generate unique token ID
    jti = secrets.token_urlsafe(32)

    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": jti,
            "type": "refresh",
        }
    )

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Check if token is blacklisted
        if redis_client:
            jti = payload.get("jti")
            if jti and redis_client.exists(f"blacklisted_token:{jti}"):
                return None

        return payload
    except JWTError:
        return None


def blacklist_token(token: str) -> None:
    """
    Blacklist a token by storing its JTI in Redis.

    Args:
        token: JWT token string to blacklist
    """
    if not redis_client:
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")

        if jti and exp:
            # Store blacklisted token until expiry
            ttl = exp - int(datetime.utcnow().timestamp())
            if ttl > 0:
                redis_client.setex(f"blacklisted_token:{jti}", ttl, "1")
    except JWTError:
        pass


def generate_token_data(user_id: int, email: str, user_type: str) -> Dict[str, Any]:
    """
    Generate token payload data.

    Args:
        user_id: User ID
        email: User email
        user_type: User type (CUSTOMER or BUSINESS_OWNER)

    Returns:
        Token payload dictionary
    """
    return {
        "sub": str(user_id),
        "email": email,
        "user_type": user_type,
    }

