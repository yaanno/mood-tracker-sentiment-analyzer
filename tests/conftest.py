import pytest
from fastapi.testclient import TestClient
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock, AsyncMock

from sentiment_analyser.main import app
from sentiment_analyser.services.sentiment.analyzer import SentimentAnalyzer
from sentiment_analyser.services.sentiment.service import SentimentService


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Fixture that creates a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_sentiment_analyzer() -> Generator[MagicMock, None, None]:
    """Fixture that creates a mock sentiment analyzer."""
    analyzer = MagicMock(spec=SentimentAnalyzer)
    analyzer.analyze = AsyncMock(return_value={"polarity": 0.5, "subjectivity": 0.5})
    yield analyzer


@pytest.fixture
async def mock_sentiment_service(
    mock_sentiment_analyzer: MagicMock,
) -> AsyncGenerator[SentimentService, None]:
    """Fixture that creates a mock sentiment service with the mock analyzer."""
    service = SentimentService(analyzer=mock_sentiment_analyzer)
    yield service
