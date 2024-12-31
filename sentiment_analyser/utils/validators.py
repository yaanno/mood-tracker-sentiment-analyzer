"""Input validation utilities for sentiment analysis.

This module provides functions for validating input text and parameters
used in sentiment analysis operations.
"""

from typing import Optional, Tuple

# Constants for validation
MIN_TEXT_LENGTH = 1
MAX_TEXT_LENGTH = 1000


def validate_text(
    text: str, min_length: int = MIN_TEXT_LENGTH, max_length: int = MAX_TEXT_LENGTH
) -> Tuple[bool, Optional[str]]:
    """Validate input text for sentiment analysis.

    Args:
        text: Input text to validate
        min_length: Minimum allowed text length
        max_length: Maximum allowed text length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        return False, "Text cannot be empty"

    if len(text) < min_length:
        return False, f"Text must be at least {min_length} characters"

    if len(text) > max_length:
        return False, f"Text cannot exceed {max_length} characters"

    return True, None
