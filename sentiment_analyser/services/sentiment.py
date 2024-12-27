from typing import Optional
from transformers import pipeline
from fastapi import HTTPException

from sentiment_analyser.core.config import get_settings
from sentiment_analyser.core.logging import get_logger
from sentiment_analyser.models.schema import SentimentResponse, EmotionScore

settings = get_settings()
logger = get_logger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        try:
            self.model = pipeline(
                task="sentiment-analysis",
                model=settings.model.MODEL_NAME,
                device=-1  # CPU
            )
            logger.info(f"Model {settings.model.MODEL_NAME} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable: Failed to initialize model"
            )

    def analyze(self, text: str) -> SentimentResponse:
        try:
            # Get predictions from model
            results = self.model(text, top_k=None)  # Get all possible labels
            
            logger.debug(f"Raw model output: {results}")
            
            if not results or not isinstance(results, list):
                logger.error(f"Invalid model output format: {results}")
                raise ValueError("Invalid model output format")

            # Convert predictions to EmotionScore objects
            scores = []
            for pred in results:
                if 'label' not in pred or 'score' not in pred:
                    logger.error(f"Missing required fields in prediction: {pred}")
                    continue
                    
                scores.append(EmotionScore(
                    label=pred['label'].lower(),
                    score=float(pred['score'])
                ))
            
            if not scores:
                logger.error("No valid predictions found")
                raise ValueError("No valid sentiment predictions")

            # Create response with all scores
            return SentimentResponse(
                text=text,
                scores=scores
            )
        except Exception as e:
            logger.error(f"Error during sentiment analysis: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error processing sentiment analysis"
            )

_analyzer: Optional[SentimentAnalyzer] = None

def get_sentiment_analyzer() -> SentimentAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer