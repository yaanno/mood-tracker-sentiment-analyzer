from fastapi import APIRouter, Depends
from sentiment_analyser.models.schema import SentimentRequest, SentimentResponse
from sentiment_analyser.services.sentiment import SentimentAnalyzer, get_sentiment_analyzer
from sentiment_analyser.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(
    request: SentimentRequest,
    analyzer: SentimentAnalyzer = Depends(get_sentiment_analyzer)
) -> SentimentResponse:
    logger.info(f"Analyzing sentiment for text: {request.text[:50]}...")
    return analyzer.analyze(request.text)