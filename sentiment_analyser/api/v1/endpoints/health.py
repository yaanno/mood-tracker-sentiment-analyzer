import time
from typing import Dict

from fastapi import APIRouter, Depends, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from sentiment_analyser.core.config import get_settings
from sentiment_analyser.core.logging import get_logger
from sentiment_analyser.models.schema import HealthResponse
from sentiment_analyser.services.sentiment import get_sentiment_analyzer

settings = get_settings()
router = APIRouter()
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)

async def get_process_time(response: Response) -> None: # type: ignore
    """Add X-Process-Time header to track API response time."""
    start_time = time.time()
    yield
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

@limiter.limit("10/minute")
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
        analyzer = get_sentiment_analyzer()
        model_status = analyzer is not None
        
        health_info = {
            "status": "healthy" if model_status else "degraded",
            "version": settings.app.VERSION,
            "model_loaded": model_status,
        }
        
        logger.info(
            "Health check completed",
            extra={
                "status": health_info["status"],
                "version": health_info["version"],
                "model_loaded": health_info["model_loaded"]
            }
        )
        
        return health_info
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "version": settings.app.VERSION,
            "model_loaded": False
        }
