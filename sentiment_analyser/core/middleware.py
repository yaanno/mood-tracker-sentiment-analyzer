"""Middleware components for request processing and error handling."""

import time

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from sentiment_analyser.core.errors import SentimentAnalyzerError, to_http_error
from sentiment_analyser.core.logging import get_logger

from .security import SecurityMiddleware

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


def get_limiter() -> Limiter:
    """Get the global rate limiter instance.

    Returns:
        The configured Limiter instance
    """
    return limiter


def setup_middleware(app: FastAPI) -> None:
    """Configure and add middleware to FastAPI application.

    Args:
        app: The FastAPI application instance
    """
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
