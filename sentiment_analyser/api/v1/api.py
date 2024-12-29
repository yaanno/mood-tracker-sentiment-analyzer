from fastapi import APIRouter
from sentiment_analyser.api.v1.endpoints import health, sentiment
from sentiment_analyser.core.settings import get_settings

settings = get_settings()

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(sentiment.router, prefix="/sentiment", tags=["sentiment"])
