"""Custom exception definitions for the sentiment analyzer service."""
from http import HTTPStatus
from typing import Any, Dict, Optional

class SentimentAnalyzerError(Exception):
    """Base exception for all sentiment analyzer errors."""
    
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(SentimentAnalyzerError):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=HTTPStatus.BAD_REQUEST,
            details=details
        )

class ModelError(SentimentAnalyzerError):
    """Raised when the ML model encounters an error."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            code="MODEL_ERROR",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            details=details
        )

class ServiceError(SentimentAnalyzerError):
    """Raised when a service operation fails."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            code="SERVICE_ERROR",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            details=details
        )

class RateLimitError(SentimentAnalyzerError):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            code="RATE_LIMIT_ERROR",
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            details=details
        )

