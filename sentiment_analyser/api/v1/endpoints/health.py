import time
from typing import Dict
from fastapi import APIRouter, Depends, Request, Response
from sentiment_analyser.core.settings import get_settings
from sentiment_analyser.core.logging import get_logger
from sentiment_analyser.models.api.schema import HealthResponse
from sentiment_analyser.services.sentiment.service import get_sentiment_service
from sentiment_analyser.core.middleware import get_limiter

settings = get_settings()
router = APIRouter()
logger = get_logger(__name__)
limiter = get_limiter()


async def get_process_time(response: Response) -> None:  # type: ignore
    """Add X-Process-Time header to track API response time."""
    start_time = time.time()
    yield
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)


@limiter.limit("120/minute")
@router.get(
    "",
    response_model=HealthResponse,
    dependencies=[Depends(get_process_time)],
)
async def health_check(request: Request) -> Dict:
    """
    Check system health including:
    - System status
    - Model availability
    - Version information
    """
    try:
        analyzer = get_sentiment_service()
        model_status = analyzer is not None

        rate_limit_info = {
            "limit": "120/minute",
            "remaining": request.headers.get("X-RateLimit-Remaining", "N/A"),
            "reset": request.headers.get("X-RateLimit-Reset", "N/A"),
        }
        health_info = {
            "rate_limit": rate_limit_info,
            "status": "healthy" if model_status else "degraded",
            "version": settings.app.VERSION,
            "model_loaded": model_status,
            "environment": settings.app.ENVIRONMENT,
        }

        logger.info(
            "Health check completed",
            extra={
                "status": health_info["status"],
                "version": health_info["version"],
                "model_loaded": health_info["model_loaded"],
            },
        )
        return health_info
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "version": settings.app.VERSION,
            "model_loaded": False,
        }
