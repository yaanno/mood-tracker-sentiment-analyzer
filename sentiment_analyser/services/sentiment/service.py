"""Service layer for sentiment analysis orchestration."""

from typing import Optional

from fastapi import HTTPException

from sentiment_analyser.core.logging import get_logger
from sentiment_analyser.models.api.schema import SentimentResponse
from sentiment_analyser.utils.errors import CacheError

from .analyzer import SentimentAnalyzer
from .cache import SentimentCache

logger = get_logger(__name__)


class SentimentService:
    """Service class orchestrating sentiment analysis."""

    def __init__(self):
        """Initialize sentiment analysis service with analyzer and cache."""
        self.analyzer: Optional[SentimentAnalyzer] = None
        self.cache: Optional[SentimentCache] = None

    async def analyze_sentiment(self, text: str) -> SentimentResponse:
        """Analyze sentiment of text, using cache when available.

        Args:
            text: Input text to analyze

        Returns:
            SentimentResponse containing analysis results

        Raises:
            HTTPException: On analysis failure
        """
        try:
            # Check cache first
            cached_scores = None
            if self.cache is not None:
                try:
                    cached_scores = self.cache.get(text)
                except CacheError as e:
                    logger.error(f"Cache error: {str(e)}")
                if cached_scores is not None:
                    logger.info("Using cached sentiment analysis")
                    return SentimentResponse(text=text, scores=cached_scores)

            # Perform new analysis
            if self.analyzer is None:
                raise HTTPException(
                    status_code=500, detail="SentimentAnalyzer is not initialized"
                )
            scores = self.analyzer.analyze_text(text)

            # Cache results
            if self.cache is not None:
                try:
                    self.cache.set(text, scores)
                except CacheError as e:
                    logger.error(f"Cache error: {str(e)}")

            return SentimentResponse(text=text, scores=scores)

        except Exception as e:
            logger.error(f"Service error during analysis: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error processing sentiment analysis: {str(e)}"
            )


# Singleton instance
_service: Optional[SentimentService] = None


def get_sentiment_service() -> SentimentService:
    """Get or create singleton service instance.

    Returns:
        Singleton SentimentService instance
    """
    global _service
    if _service is None:
        _service = SentimentService()
    return _service


# FastAPI dependency
async def get_service() -> SentimentService:
    """FastAPI dependency for getting service instance.

    Returns:
        Singleton SentimentService instance
    """
    return get_sentiment_service()


async def startup():
    """Start up the service and its components."""
    service = get_sentiment_service()
    service.analyzer = SentimentAnalyzer()
    service.cache = SentimentCache()
    await service.cache.start()
    logger.info("Service components started")


async def shutdown():
    """Shut down the service and clean up resources."""
    service = get_sentiment_service()
    if service.cache:
        await service.cache.stop()
    if service.analyzer:
        service.analyzer.cleanup()
    logger.info("Service components shut down")
