from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from sentiment_analyser.api.v1.api import api_router
from sentiment_analyser.core.settings import get_settings
from sentiment_analyser.core.logging import get_logger
from sentiment_analyser.core.middleware import setup_middleware

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Starting up application...")
    # setup_logging()
    # Add any startup code here (database connections, model loading etc.)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    # Add any cleanup code here

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app.PROJECT_NAME,
        version=settings.app.VERSION,
        openapi_url=f"{settings.app.API_PREFIX}/openapi.json",
        lifespan=lifespan,
        docs_url=f"{settings.app.API_PREFIX}/docs",
        redoc_url=f"{settings.app.API_PREFIX}/redoc"
    )

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
            description="Sentiment Analysis API with rate limiting and proper error handling",
            routes=app.routes,
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
    return app

app = create_application()
