"""Caching layer for sentiment analysis results."""
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json
from pathlib import Path

from sentiment_analyser.core.logging import get_logger
from sentiment_analyser.models.api.schema import EmotionScore

logger = get_logger(__name__)

class SentimentCache:
    """Cache for sentiment analysis results."""
    
    def __init__(self, ttl_minutes: int = 60):
        """Initialize the cache.
        
        Args:
            ttl_minutes: Time-to-live for cache entries in minutes
        """
        self.cache: Dict[str, Dict] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        
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

