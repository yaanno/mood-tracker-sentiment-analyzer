from fastapi import APIRouter, Depends, HTTPException
from sentiment_analyser.core.config import get_settings
from sentiment_analyser.models.schema import SentimentRequest, SentimentResponse
from sentiment_analyser.services.sentiment import SentimentAnalyzer, get_sentiment_analyzer
from sentiment_analyser.core.logging import get_logger
import time
import uuid
from typing import Dict, Any

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()

@router.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(
    request: SentimentRequest,
    analyzer: SentimentAnalyzer = Depends(get_sentiment_analyzer)
) -> SentimentResponse:
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    
    logger.info(
        f"Request {request_id}: Starting sentiment analysis",
        extra={
            "request_id": request_id,
            "text_length": len(request.text),
            "text_preview": request.text[:50]
        }
    )
    
    try:
        # Perform sentiment analysis
        result = analyzer.analyze(request.text)
        
        # Calculate processing time
        processing_time = time.perf_counter() - start_time
        
        # Add metadata to response
        metadata: Dict[str, Any] = {
            "request_id": request_id,
            "processing_time_ms": round(processing_time * 1000, 2),
            "model_info": analyzer.model_name if hasattr(analyzer, 'model_name') else "default_model",
            "text_length": len(request.text)
        }
        
        logger.info(
            f"Request {request_id}: Analysis completed successfully",
            extra={
                "request_id": request_id,
                "processing_time_ms": metadata["processing_time_ms"],
                "score": result.scores
            }
        )
        
        return SentimentResponse(
            text=request.text,
            scores=result.scores,
            metadata=metadata,
            model_name=settings.model.MODEL_NAME
        )
        
    except ValueError as e:
        logger.error(
            f"Request {request_id}: Invalid input",
            extra={"request_id": request_id, "error": str(e)}
        )
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(
            f"Request {request_id}: Internal server error",
            extra={"request_id": request_id, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the request"
        )
