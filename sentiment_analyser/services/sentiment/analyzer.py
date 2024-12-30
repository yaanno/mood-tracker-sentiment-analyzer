"""Core implementation of sentiment analysis using transformers models."""

from typing import List, Optional

from fastapi import HTTPException
from transformers import pipeline

from sentiment_analyser.core.errors import (
    ModelError,
    SentimentAnalyzerError,
    ServiceError,
)
from sentiment_analyser.core.logging import get_logger
from sentiment_analyser.core.settings import get_settings
from sentiment_analyser.models.api.schema import EmotionScore

settings = get_settings()
logger = get_logger(__name__)


class SentimentAnalyzer:
    """Core sentiment analysis implementation using transformers."""

    def __init__(self, model_name: str = settings.model.MODEL_NAME, device: int = -1):
        """Initialize the sentiment analyzer.

        Args:
            model_name: The name of the model to use for analysis
            device: Device ID to run model on (-1 for CPU)

        Raises:
            ModelError: If model initialization fails
        """
        self.model_name = model_name
        try:
            self.model = pipeline(
                task="sentiment-analysis", model=model_name, device=device
            )
            logger.info(f"Model {model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            raise ModelError("Failed to initialize model")

    def reload_model(self, model_name: Optional[str] = None, device: int = -1):
        """Reload the sentiment analysis model.

        Args:
            model_name: Optional new model name to load
            device: Device ID to run model on (-1 for CPU)
        """
        if model_name:
            self.model_name = model_name
        try:
            self.model = pipeline(
                task="sentiment-analysis", model=self.model_name, device=device
            )
            logger.info(f"Model {self.model_name} reloaded successfully")
        except Exception as e:
            logger.error(f"Failed to reload model: {str(e)}")
            raise ServiceError(
                "Service temporarily unavailable: Failed to reload model",
            )

    def analyze_text(self, text: str) -> List[EmotionScore]:
        """Analyze the sentiment of the given text.

        Args:
            text: Input text to analyze

        Returns:
            List of EmotionScore objects with sentiment predictions

        Raises:
            ValueError: If model output is invalid
            TextProcessingError: If analysis fails
        """
        try:
            results = self.model(text, top_k=None)
            # logger.debug(f"Raw model output: {results}")

            if not results or not isinstance(results, list):
                logger.error(f"Invalid model output format: {results}")
                raise ModelError("Invalid model output format")

            scores = []
            for pred in results:
                if "label" not in pred or "score" not in pred:
                    logger.error(f"Missing required fields in prediction: {pred}")
                    continue

                scores.append(
                    EmotionScore(
                        label=pred["label"].lower(), score=float(pred["score"])
                    )
                )

            if not scores:
                logger.error("No valid predictions found")
                raise ModelError("No valid sentiment predictions")

            return scores

        except SentimentAnalyzerError as e:
            logger.error(f"Error during sentiment analysis: {str(e)}")
            # raise ServiceError("Error processing sentiment analysis")
            raise HTTPException(status_code=e.status_code, detail=str(e))

    def cleanup(self):
        """Clean up model resources."""
        if hasattr(self, "model"):
            del self.model
            logger.info("Cleaned up transformer model resources")

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self):
        """Context manager exit."""
        self.cleanup()
