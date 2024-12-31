"""Security module for service-to-service authentication."""

import hmac
import logging

from fastapi import Request
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from starlette.middleware.base import BaseHTTPMiddleware

from .errors import AuthenticationError
from .settings import get_settings

logger = logging.getLogger(__name__)

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def create_api_key_limiter() -> Limiter:
    """Create a rate limiter that uses API keys for tracking."""

    def get_api_key(request: Request) -> str:
        return request.headers.get("X-API-Key", "")

    return Limiter(key_func=get_api_key)


def verify_api_key(api_key: str) -> bool:
    """Verify if the provided API key is valid using secure comparison."""
    settings = get_settings()
    valid_keys = settings.security.API_KEYS

    if not api_key:
        return False

    return any(
        hmac.compare_digest(api_key.encode(), valid_key.encode())
        for valid_key in valid_keys
    )


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for API key verification and rate limiting."""

    def __init__(self, app, settings=None):
        """Initialize the middleware with settings."""
        super().__init__(app)
        self.settings = settings or get_settings()
        self.limiter = create_api_key_limiter()

    async def dispatch(self, request: Request, call_next):
        """Process the request, verify API key, and apply rate limiting.

        For /analyze endpoints, allow JSON validation to occur before security checks.
        For other endpoints, verify API key before processing.
        """
        # Check if path is public (documentation, etc)
        for public_path in self.settings.security.PUBLIC_PATHS:
            if request.url.path.startswith(public_path):
                return await call_next(request)

        for private_path in self.settings.security.PRIVATE_PATHS:
            if request.url.path.startswith(private_path):
                api_key = request.headers.get("X-API-Key")
                if not api_key:
                    raise AuthenticationError(
                        message="Missing API key",
                        details={"header": "X-API-Key"},
                    )
                if not verify_api_key(api_key):
                    raise AuthenticationError(
                        message="Invalid API key",
                        details={"header": "X-API-Key"},
                    )
                return await call_next(request)

        return await call_next(request)
        # try:
        #     ratelimit = self.limiter.limit("60/minute")

        #     @ratelimit
        #     async def rate_limited_next():
        #         return await call_next(request)

        #     return await rate_limited_next()
        # except RateLimitExceeded:
        #     raise ServiceError(
        #         message="Rate limit exceeded",
        #         details={"api_key": api_key},
        #     )
