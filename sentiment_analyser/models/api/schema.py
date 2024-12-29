from enum import Enum
from typing import List, Optional 
from pydantic import BaseModel, Field, field_validator, ConfigDict

class EmotionType(str, Enum):
    """Available emotion types returned by the model."""
    ADMIRATION = "admiration"
    AMUSEMENT = "amusement"
    ANGER = "anger"
    ANNOYANCE = "annoyance"
    APPROVAL = "approval"
    CARING = "caring"
    CONFUSION = "confusion"
    CURIOSITY = "curiosity"
    DESIRE = "desire"
    DISAPPOINTMENT = "disappointment"
    DISAPPROVAL = "disapproval"
    DISGUST = "disgust"
    EMBARRASSMENT = "embarrassment"
    EXCITEMENT = "excitement"
    FEAR = "fear"
    GRATITUDE = "gratitude"
    GRIEF = "grief"
    JOY = "joy"
    LOVE = "love"
    NERVOUSNESS = "nervousness"
    OPTIMISM = "optimism"
    PRIDE = "pride"
    REALIZATION = "realization"
    RELIEF = "relief"
    REMORSE = "remorse"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    NEUTRAL = "neutral"

class StatusEnum(str, Enum):
    """Enumeration for API response status values."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class HealthEnum(str, Enum):
    """Enumeration for API response health values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class SentimentRequest(BaseModel):
    """
    Request model for sentiment analysis.
    
    Attributes:
        text: The input text to analyze for sentiment
    """
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)
    
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Text to analyze for sentiment (1-1000 characters)",
        examples=["This is great!"]
    )

    @field_validator('text')
    def validate_text_content(cls, v: str) -> str:
        """Validate that the text contains actual words and is not just symbols or whitespace."""
        # Remove whitespace for checking
        stripped = v.strip()
        
        # Check if text is empty after stripping
        if not stripped:
            raise ValueError("Text cannot be empty or contain only whitespace")
        return stripped

class EmotionScore(BaseModel):
    """
    Individual emotion score from the analysis.

    Attributes:
        label: The emotion type from predefined emotions
        score: Confidence score between 0 and 1
    """
    model_config = ConfigDict(validate_default=True)

    label: EmotionType = Field(
        ...,
        description="Emotion type",
        examples=["joy", "sadness", "anger"]
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the emotion",
        examples=[0.95]
    )

class SentimentResponse(BaseModel):
    """
    Response model for sentiment analysis.

    Attributes:
        text: The input text that was analyzed
        scores: List of emotion scores for all detected emotions
        status: Analysis status (success/error/warning)
        message: Detailed status message
        model_name: Optional name of the model used for analysis
    """
    text: str = Field(
        ...,
        description="The input text that was analyzed"
    )
    scores: List[EmotionScore] = Field(
        ...,
        description="List of emotion scores sorted by confidence",
        min_length=1
    )
    status: StatusEnum = Field(
        default=StatusEnum.SUCCESS,
        description="Analysis status"
    )
    message: str = Field(
        default="Analysis completed successfully",
        description="Status message"
    )
    model_name: Optional[str] = Field(
        default=None,
        description="Name of the model used for analysis"
    )
    
    @field_validator('scores')
    def sort_scores(cls, v: List[EmotionScore]) -> List[EmotionScore]:
        """Sort emotion scores by confidence in descending order."""
        return sorted(v, key=lambda x: x.score, reverse=True)

class HealthResponse(BaseModel):
    """
    Response model for health check endpoint.
    
    Attributes:
        status: Service status (up/down)
        version: API version
        model_loaded: Whether the ML model is loaded and ready
        model_name: Name of the loaded model
        environment: Current environment (dev/prod)
    """
    status: HealthEnum = Field(
        ...,
        description="Service status"
    )
    version: str = Field(
        ...,
        pattern=r"^\d+\.\d+\.\d+$",
        description="API version",
        examples=["1.0.0"]
    )
    model_loaded: bool = Field(
        ...,
        description="Whether the ML model is loaded and ready"
    )
    model_name: Optional[str] = Field(
        default=None,
        description="Name of the loaded model"
    )
    environment: str = Field(
        ...,
        description="Current environment (dev/prod)",
        examples=["development", "production"]
    )
