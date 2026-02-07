"""Password hashing and simple token management."""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import bcrypt
import secrets
import hashlib
import logging
from uuid import UUID
from sqlalchemy.orm import Session

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


def generate_simple_token() -> str:
    """
    Generate cryptographically secure random token.

    Returns:
        Random token string (64 characters)
    """
    return f"tok_{secrets.token_urlsafe(48)}"


def hash_token(token: str) -> str:
    """
    Hash token using SHA256 for secure storage.

    Args:
        token: Plain token string

    Returns:
        SHA256 hash of token (hex string)
    """
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(
    db: Session,
    user_id: UUID,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    expires_hours: int = 24,
) -> str:
    """
    Create and store access token in database.

    Args:
        db: Database session
        user_id: User ID (UUID)
        ip_address: Client IP address (optional, for security tracking)
        user_agent: Client user agent (optional, for security tracking)
        expires_hours: Token expiration in hours (default 24)

    Returns:
        Plain token string (to send to client)
    """
    from app.models.access_token import AccessToken

    # Generate plain token (client will receive this)
    plain_token = generate_simple_token()

    # Hash token for database storage (security best practice)
    token_hash = hash_token(plain_token)

    # Calculate expiration
    expires_at = datetime.utcnow() + timedelta(hours=expires_hours)

    # Create token record
    access_token = AccessToken(
        user_id=user_id,
        token_hash=token_hash,
        ip_address=ip_address[:45] if ip_address else None,  # Truncate to fit column
        user_agent=user_agent[:512] if user_agent else None,  # Truncate to fit column
        expires_at=expires_at,
    )

    db.add(access_token)
    db.commit()
    db.refresh(access_token)

    logger.info(f"Access token created for user {user_id}, expires at {expires_at}")

    return plain_token  # Return plain token to send to client


def validate_token(
    db: Session,
    token: str,
    check_ip: Optional[str] = None,
    check_user_agent: Optional[str] = None,
):
    """
    Validate token and return associated user.

    Args:
        db: Database session
        token: Plain token string from client
        check_ip: Optional IP to validate against stored IP
        check_user_agent: Optional user agent to validate

    Returns:
        User object if token is valid, None otherwise
    """
    from app.models.access_token import AccessToken
    from app.models.user import User

    # Hash the incoming token to compare with database
    token_hash = hash_token(token)

    # Query token from database
    token_record = (
        db.query(AccessToken)
        .filter(
            AccessToken.token_hash == token_hash,
            AccessToken.expires_at > datetime.utcnow(),  # Check expiration
        )
        .first()
    )

    if not token_record:
        logger.warning(f"Invalid or expired token attempted")
        return None

    # Optional: Check IP address for suspicious activity
    if check_ip and token_record.ip_address:
        if token_record.ip_address != check_ip:
            logger.warning(
                f"Token used from different IP. "
                f"Original: {token_record.ip_address}, Current: {check_ip}"
            )
            # Don't block, but log for security monitoring
            # In production, you might want to send alert email

    # Get and return user
    user = db.query(User).filter(User.id == token_record.user_id).first()

    if user:
        logger.debug(f"Token validated for user {user.id}")

    return user


def revoke_token(db: Session, token: str) -> bool:
    """
    Revoke (delete) a token from database.

    Args:
        db: Database session
        token: Plain token string

    Returns:
        True if token was revoked, False if not found
    """
    from app.models.access_token import AccessToken

    token_hash = hash_token(token)

    result = db.query(AccessToken).filter(AccessToken.token_hash == token_hash).delete()
    db.commit()

    if result > 0:
        logger.info(f"Token revoked successfully")
        return True

    logger.warning(f"Attempted to revoke non-existent token")
    return False


def revoke_all_user_tokens(db: Session, user_id: UUID) -> int:
    """
    Revoke all tokens for a specific user.

    Useful for logout from all devices or security incidents.

    Args:
        db: Database session
        user_id: User ID (UUID)

    Returns:
        Number of tokens revoked
    """
    from app.models.access_token import AccessToken

    count = db.query(AccessToken).filter(AccessToken.user_id == user_id).delete()
    db.commit()

    logger.info(f"Revoked {count} tokens for user {user_id}")
    return count


def cleanup_expired_tokens(db: Session) -> int:
    """
    Delete all expired tokens from database.

    Should be run periodically (e.g., daily cron job).

    Args:
        db: Database session

    Returns:
        Number of tokens deleted
    """
    from app.models.access_token import AccessToken

    count = (
        db.query(AccessToken)
        .filter(AccessToken.expires_at < datetime.utcnow())
        .delete()
    )
    db.commit()

    logger.info(f"Cleaned up {count} expired tokens")
    return count


def get_active_sessions(db: Session, user_id: UUID) -> int:
    """
    Get count of active sessions for a user.

    Args:
        db: Database session
        user_id: User ID (UUID)

    Returns:
        Number of active (non-expired) tokens
    """
    from app.models.access_token import AccessToken

    count = (
        db.query(AccessToken)
        .filter(
            AccessToken.user_id == user_id,
            AccessToken.expires_at > datetime.utcnow(),
        )
        .count()
    )

    return count

