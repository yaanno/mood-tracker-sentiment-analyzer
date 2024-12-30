import time
import uuid
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request

from sentiment_analyser.core.exceptions import (
    RateLimitError,
    ServiceError,
    ValidationError,
)
from sentiment_analyser.core.logging import get_logger
from sentiment_analyser.core.middleware import get_limiter
from sentiment_analyser.core.settings import get_settings
from sentiment_analyser.models.api.schema import SentimentRequest, SentimentResponse
from sentiment_analyser.services.sentiment.service import get_service

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()
limiter = get_limiter()


@limiter.limit("60/minute")
@router.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(
    request: SentimentRequest,
    req: Request,
) -> SentimentResponse:
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    logger.info(
        f"Request {request_id}: Starting sentiment analysis",
        extra={
            "request_id": request_id,
            "text_length": len(request.text),
            "text_preview": request.text[:50],
        },
    )
    try:
        # TODO: Not ideal but works atm
        analyzer = await get_service()
        # Perform sentiment analysis
        result = await analyzer.analyze_sentiment(request.text)
        # Calculate processing time
        processing_time = time.perf_counter() - start_time
        # Add metadata to response
        metadata: Dict[str, Any] = {
            "rate_limit": {
                "limit": "60/minute",
                "remaining": req.headers.get("X-RateLimit-Remaining", "N/A"),
                "reset": req.headers.get("X-RateLimit-Reset", "N/A"),
            },
            "request_id": request_id,
            "processing_time_ms": round(processing_time * 1000, 2),
            "model_name": (
                settings.model.MODEL_NAME
                if hasattr(analyzer, "model_name")
                else "default_model"
            ),
            "text_length": len(request.text),
        }
        logger.info(
            f"Request {request_id}: Analysis completed successfully",
            extra={
                "request_id": request_id,
                "processing_time_ms": metadata["processing_time_ms"],
                "score": result.scores,
            },
        )
        return SentimentResponse(
            text=request.text,
            scores=result.scores,
            # metadata=metadata,
            model_name=settings.model.MODEL_NAME,
        )
    except ValidationError as e:
        logger.error(
            f"Request {request_id}: Invalid input",
            extra={"request_id": request_id, "error": str(e)},
        )
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except RateLimitError as e:
        logger.warning(
            f"Request {request_id}: Rate limit exceeded",
            extra={"request_id": request_id},
        )
        raise HTTPException(
            status_code=e.status_code,
            detail="Rate limit exceeded. Please try again later.",
        )
    except ServiceError as error:
        logger.error(
            f"Request {request_id}: Internal server error",
            extra={"request_id": request_id, "error": str(error)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=error.status_code,
            detail="An error occurred while processing the request",
        )
