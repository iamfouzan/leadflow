"""Custom validators."""
import re
from typing import Optional


def validate_password(password: str) -> bool:
    """
    Validate password strength.

    Args:
        password: Password string

    Returns:
        True if password is valid, False otherwise
    """
    if len(password) < 8:
        return False

    # Check for at least one digit
    if not re.search(r"\d", password):
        return False

    # Check for at least one letter
    if not re.search(r"[a-zA-Z]", password):
        return False

    return True


def sanitize_phone(phone: Optional[str]) -> Optional[str]:
    """
    Sanitize phone number by removing non-digit characters.

    Args:
        phone: Phone number string

    Returns:
        Sanitized phone number or None
    """
    if not phone:
        return None

    # Remove all non-digit characters
    cleaned = re.sub(r"\D", "", phone)
    if len(cleaned) < 10:
        return None

    return cleaned

