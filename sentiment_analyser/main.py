from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
import logging
from typing import List
from transformers.pipelines.base import Pipeline
from transformers import pipeline

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Mood Tracker Sentiment Analysis API",
    description="Microservice to analyze text to enhance user provided mood tags based on notes.",
    version="1.0.0"
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, headers: dict[str, str] | None = None):
        super().__init__(app)
        self.headers = headers or {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            "Pragma": "no-cache",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
        }

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        for header_key, header_value in self.headers.items():
            response.headers[header_key] = header_value
        return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,
)

app.add_middleware(SecurityHeadersMiddleware)

# Add security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Configure for production
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = []
    for error in exc.errors():
        error_location = " -> ".join(str(loc) for loc in error["loc"])
        error_details.append(f"{error_location}: {error['msg']}")
    
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            status="error",
            code=422,
            message="Request validation failed",
            details=error_details
        ).model_dump()
    )
# Define the data model for the request body
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorResponse(BaseModel):
    status: str = "error"
    code: int
    message: str
    details: List[str] | None = None

class TextData(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)

    @field_validator('text', mode='before')
    def text_must_be_valid(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('The provided text cannot be empty or contain only whitespace characters')
        return value.strip()

class EmotionScore(BaseModel):
    label: str
    score: float

class SentimentResponse(BaseModel):
    sentiment: List[EmotionScore]
    status: str = "success"
    message: str = "Analysis completed successfully"

# Initialize the sentiment analysis pipeline
classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

@app.get("/")
def index():
    return {"message": "app root"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": app.version
    }

@app.post(
    "/analyze",
    response_model=SentimentResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/TextData"},
                    "maxLength": 16384  # 16KB limit
                }
            }
        }
    }
)
@limiter.limit("10/minute")
async def analyse(request: Request, data: TextData) -> SentimentResponse:
    """
    Analyze the sentiment of the provided text.

    Args:
        data: TextData object containing the text to analyze

    Returns:
        SentimentResponse: Object containing emotion scores and status

    Raises:
        HTTPException: If text processing or model prediction fails
    """
    try:
        logger.info(f"Processing text analysis request (length: {len(data.text)})")
        
        if not isinstance(classifier, Pipeline):
            logger.error("Sentiment classifier not properly initialized")
            raise HTTPException(
                status_code=503,
                detail="Sentiment analysis service is not available"
            )

        prediction = classifier(data.text)
        sentiment_scores = [
            EmotionScore(label=item["label"], score=item["score"])
            for item in prediction[0]
        ]
        
        logger.info("Successfully completed sentiment analysis")
        return SentimentResponse(
            sentiment=sentiment_scores,
            status="success",
            message="Analysis completed successfully"
        )

    except ValueError as e:
        logger.error(f"Input validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error during sentiment analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during sentiment analysis"
        )
