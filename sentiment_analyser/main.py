from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from sentiment_analyser.api.v1.api import api_router
from sentiment_analyser.core.settings import get_settings
from sentiment_analyser.core.logging import get_logger
from sentiment_analyser.core.middleware import setup_middleware
from sentiment_analyser.core.middleware import get_limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

settings = get_settings()
logger = get_logger(__name__)

# Get the global rate limiter
limiter = get_limiter()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Starting up application...")
    from sentiment_analyser.services.sentiment.service import startup, shutdown

    await startup()

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await shutdown()


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app.PROJECT_NAME,
        version=settings.app.VERSION,
        openapi_url=f"{settings.app.API_PREFIX}/openapi.json",
        lifespan=lifespan,
        docs_url=f"{settings.app.API_PREFIX}/docs",
        redoc_url=f"{settings.app.API_PREFIX}/redoc",
    )

    # Set up rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Set up middlewares
    setup_middleware(app)

    # Include API router
    app.include_router(api_router, prefix=settings.app.API_PREFIX)

    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=settings.app.PROJECT_NAME,
            version=settings.app.VERSION,
            description="Sentiment Analysis API",
            routes=app.routes,
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
    return app


app = create_application()
