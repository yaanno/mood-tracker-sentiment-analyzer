"""Input validation utilities for sentiment analysis.

This module provides functions for validating input text and parameters
used in sentiment analysis operations.
"""
from typing import Optional, Tuple

# Constants for validation
MIN_TEXT_LENGTH = 1
MAX_TEXT_LENGTH = 5000
SUPPORTED_LANGUAGES = {"en", "es", "fr", "de", "it"}

def validate_text(
    text: str, 
    min_length: int = MIN_TEXT_LENGTH,
    max_length: int = MAX_TEXT_LENGTH
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

def validate_language(language: str) -> Tuple[bool, Optional[str]]:
    """Validate language code.

    Args:
        language: ISO language code to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not language:
        return False, "Language code is required"
        
    if language.lower() not in SUPPORTED_LANGUAGES:
        return False, f"Language {language} is not supported. Must be one of: {', '.join(SUPPORTED_LANGUAGES)}"
        
    return True, None

def validate_confidence_threshold(threshold: float) -> Tuple[bool, Optional[str]]:
    """Validate confidence threshold value.

    Args:
        threshold: Confidence threshold to validate (0.0 to 1.0)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not 0.0 <= threshold <= 1.0:
        return False, "Confidence threshold must be between 0.0 and 1.0"
    return True, None

