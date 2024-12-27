from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentiment_analyser.api.v1.api import api_router
from sentiment_analyser.core.config import get_settings
from sentiment_analyser.core.logging import get_logger
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

settings = get_settings()
logger = get_logger(__name__)


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app.PROJECT_NAME,
        version=settings.app.VERSION,
        openapi_url=f"{settings.app.API_PREFIX}/openapi.json",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.CORS_ORIGINS,
        allow_credentials=settings.api.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router, prefix=settings.app.API_PREFIX)

    return app

app = create_application()