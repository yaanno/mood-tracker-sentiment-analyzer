"""Error handling utilities and custom exceptions.

This module defines custom exceptions and error handling utilities
for the sentiment analysis service.
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException
from http import HTTPStatus

class SentimentAnalysisError(Exception):
    """Base exception for sentiment analysis errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}

class ModelLoadError(SentimentAnalysisError):
    """Raised when model loading fails."""
    pass

class TextProcessingError(SentimentAnalysisError):
    """Raised when text processing fails."""
    pass

class ValidationError(SentimentAnalysisError):
    """Raised when input validation fails."""
    pass

def handle_sentiment_error(error: Exception) -> HTTPException:
    """Convert internal errors to HTTP exceptions.

    Args:
        error: Internal exception to convert

    Returns:
        Appropriate HTTP exception
    """
    if isinstance(error, ValidationError):
        return HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=str(error)
        )
        
    if isinstance(error, ModelLoadError):
        return HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Model loading failed"
        )
        
    if isinstance(error, TextProcessingError):
        return HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=str(error)
        )
        
    # Generic error handling
    return HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred"
    )

