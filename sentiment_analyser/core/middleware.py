"""Middleware components for request processing and error handling."""

import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# from starlette.responses import Response
from sentiment_analyser.core.errors import (
    RateLimitError,
    SentimentAnalyzerError,
    to_http_error,
)
from sentiment_analyser.core.logging import get_logger

from .security import SecurityMiddleware
from .settings import get_settings

# Global rate limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
    headers_enabled=True,
    swallow_errors=False,
)

logger = get_logger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions and converting them to JSON responses."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request and handle any errors.

        Args:
            request: The incoming request
            call_next: The next middleware/endpoint to call

        Returns:
            A JSON response with error details if an error occurred,
            otherwise the normal response
        """
        try:
            return await call_next(request)

        except SentimentAnalyzerError as e:
            logger.error(
                "Error occurred: %s",
                e.message,
                extra={
                    "error_code": e.code,
                    "error_message": e.message,
                    "error_details": e.details,
                },
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": {
                        "code": e.code,
                        "message": e.message,
                        "details": e.details,
                    }
                },
            )

        except Exception as exc:
            logger.exception("Unhandled error", exc_info=exc)
            http_error = to_http_error(exc)
            return JSONResponse(
                status_code=http_error.status_code,
                content={
                    "error": http_error.detail,
                },
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request/response details."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Log request and response details.

        Args:
            request: The incoming request
            call_next: The next middleware/endpoint to call

        Returns:
            The response from the next middleware/endpoint
        """
        start_time = time.time()
        # Log request
        logger.info(
            "Incoming request",
            extra={
                "path": request.url.path,
                "method": request.method,
                "client_host": request.client.host if request.client else None,
            },
        )
        response = await call_next(request)
        # Log response
        duration = time.time() - start_time
        logger.info(
            "Request completed",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": int(duration * 1000),
            },
        )
        return response


class RateLimitState:
    """In-memory rate limit state storage."""

    def __init__(self):
        self.requests: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0.0))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with support for API keys and IP-based limiting."""

    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        self.state = RateLimitState()

    def get_rate_limit_key(self, request: Request) -> str:
        """Get rate limit key based on API key or IP address."""
        api_key = request.headers.get("X-API-Key")
        if api_key and api_key in self.settings.security.API_KEYS:
            return f"apikey:{api_key}"
        return f"ip:{get_remote_address(request)}"

    def get_rate_limit(self, request: Request) -> int:
        """Get rate limit based on authentication status."""
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return self.settings.security.API_RATE_LIMITS.get(
                api_key, self.settings.rate_limit.DEFAULT_RATE_LIMIT
            )
        return self.settings.rate_limit.DEFAULT_RATE_LIMIT

    def update_rate_limit_headers(
        self, response: Response, key: str, limit: int
    ) -> None:
        """Update response headers with rate limit information."""
        count, reset_time = self.state.requests[key]
        remaining = max(0, limit - count)
        reset_in = max(0, int(reset_time - time.time()))

        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_in)

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""
        if request.url.path in self.settings.security.PUBLIC_PATHS:
            return await call_next(request)

        key = self.get_rate_limit_key(request)
        limit = self.get_rate_limit(request)
        window = self.settings.rate_limit.WINDOW_SIZE

        # Get current state
        count, reset_time = self.state.requests[key]
        now = time.time()

        # Reset if window expired
        if now > reset_time:
            count = 0
            reset_time = now + window

        # Increment request count
        count += 1
        self.state.requests[key] = (count, reset_time)

        if count > limit:
            raise RateLimitError(
                message="Rate limit exceeded",
                details={
                    "limit": limit,
                    "window": f"{window}s",
                    "type": "api_key" if "apikey" in key else "ip",
                },
            )

        response = await call_next(request)
        self.update_rate_limit_headers(response, key, limit)
        return response


def setup_middleware(app: FastAPI) -> None:
    """Configure and add middleware to FastAPI application.

    Args:
        app: The FastAPI application instance
    """
    settings = get_settings()

    # Add security middleware first
    app.add_middleware(SecurityMiddleware)

    # Add rate limiting if enabled
    if settings.rate_limit.ENABLED:
        app.add_middleware(RateLimitMiddleware)

    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
