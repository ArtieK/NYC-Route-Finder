"""
Input validation utilities for transportation requests.
"""
import re
from typing import Tuple


def validate_address(address: str) -> Tuple[bool, str]:
    """
    Validate that an address is properly formatted.

    Args:
        address: Address string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not address or not address.strip():
        return False, "Address cannot be empty"

    if len(address) < 3:
        return False, "Address must be at least 3 characters"

    if len(address) > 200:
        return False, "Address is too long"

    return True, ""


def validate_coordinates(lat: float, lng: float) -> Tuple[bool, str]:
    """
    Validate latitude and longitude coordinates.

    Args:
        lat: Latitude value
        lng: Longitude value

    Returns:
        Tuple of (is_valid, error_message)
    """
    # NYC approximate bounds
    NYC_LAT_MIN, NYC_LAT_MAX = 40.4, 41.0
    NYC_LNG_MIN, NYC_LNG_MAX = -74.3, -73.7

    if not (NYC_LAT_MIN <= lat <= NYC_LAT_MAX):
        return False, "Latitude is outside NYC area"

    if not (NYC_LNG_MIN <= lng <= NYC_LNG_MAX):
        return False, "Longitude is outside NYC area"

    return True, ""


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: Input text to sanitize

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>\"\'`;{}]', '', text)

    return sanitized.strip()
