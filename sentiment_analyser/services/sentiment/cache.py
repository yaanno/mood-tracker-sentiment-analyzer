"""Caching layer for sentiment analysis results."""
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json, asyncio
from pathlib import Path

from sentiment_analyser.core.logging import get_logger
from sentiment_analyser.models.api.schema import EmotionScore

logger = get_logger(__name__)

class SentimentCache:
    """Cache for sentiment analysis results."""
    
    def __init__(self, ttl_minutes: int = 60, cleanup_interval: int = 5):
        """Initialize the cache.
        
        Args:
            ttl_minutes: Time-to-live for cache entries in minutes
            cleanup_interval: Interval between cleanup runs in minutes
        """
        self.cache: Dict[str, Dict] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self.cleanup_interval = timedelta(minutes=cleanup_interval)
        self.cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
    def get(self, text: str) -> Optional[List[EmotionScore]]:
        """Get cached sentiment scores if available.
        
        Args:
            text: The text to look up
            
        Returns:
            Cached EmotionScore list if available and not expired, None otherwise
        """
        if text not in self.cache:
            return None
            
        entry = self.cache[text]
        if datetime.now() - entry["timestamp"] > self.ttl:
            del self.cache[text]
            return None
            
        return [
            EmotionScore(**score)
            for score in entry["scores"]
        ]
        
    def set(self, text: str, scores: List[EmotionScore]) -> None:
        """Cache sentiment analysis results.
        
        Args:
            text: The analyzed text
            scores: The sentiment scores to cache
        """
        self.cache[text] = {
            "timestamp": datetime.now(),
            "scores": [score.dict() for score in scores]
        }
        logger.debug(f"Cached analysis for text: {text[:50]}...")

    async def start(self):
        """Start the background cleanup task."""
        if not self._running:
            self._running = True
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Started cache cleanup task")

    async def stop(self):
        """Stop the background cleanup task."""
        if self._running:
            self._running = False
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            logger.info("Stopped cache cleanup task")

    def _cleanup_expired(self):
        """Remove expired entries from cache."""
        now = datetime.now()
        expired = [
            key for key, entry in self.cache.items()
            if now - entry["timestamp"] > self.ttl
        ]
        for key in expired:
            del self.cache[key]
        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired cache entries")

    async def _cleanup_loop(self):
        """Background task for periodic cache cleanup."""
        while self._running:
            self._cleanup_expired()
            await asyncio.sleep(self.cleanup_interval.total_seconds())

    async def __aenter__(self):
        """Context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.stop()
