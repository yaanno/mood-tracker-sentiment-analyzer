"""Unified error handling for the sentiment analysis service."""

from http import HTTPStatus
from typing import Any, Dict, Optional

from fastapi import HTTPException


class SentimentAnalyzerError(Exception):
    """Base exception for all service errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ValidationError(SentimentAnalyzerError):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=HTTPStatus.BAD_REQUEST,
            details=details,
        )


class ModelError(SentimentAnalyzerError):
    """Raised when model operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="MODEL_ERROR",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            details=details,
        )


class TextProcessingError(SentimentAnalyzerError):
    """Raised when text processing fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="PROCESSING_ERROR",
            status_code=HTTPStatus.BAD_REQUEST,
            details=details,
        )


class CacheError(SentimentAnalyzerError):
    """Raised when cache operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CACHE_ERROR",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            details=details,
        )


class RateLimitError(SentimentAnalyzerError):
    """Raised when API rate limits are exceeded."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="RATE_LIMIT_ERROR",
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            details=details,
        )


class ServiceError(SentimentAnalyzerError):
    """Raised when a service operation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="SERVICE_ERROR",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            details=details,
        )


class AuthenticationError(SentimentAnalyzerError):
    """Raised when the authentication fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="AUTH_ERROR",
            status_code=HTTPStatus.UNAUTHORIZED,
            details=details,
        )


def to_http_error(error: Exception) -> HTTPException:
    """Convert any exception to an appropriate HTTP exception.

    Args:
        error: Exception to convert

    Returns:
        HTTPException with appropriate status code and details
    """
    if isinstance(error, SentimentAnalyzerError):
        return HTTPException(
            status_code=error.status_code,
            detail={
                "code": error.code,
                "message": error.message,
                "details": error.details,
            },
        )

    # Generic error handling
    return HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail={
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
        },
    )
