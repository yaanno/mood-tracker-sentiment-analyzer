from typing import AsyncGenerator
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from sentiment_analyser.main import app
from sentiment_analyser.models.api.schema import SentimentRequest, SentimentResponse


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async client fixture for testing."""
    async with AsyncClient(
        app=app, base_url="http://test", follow_redirects=True
    ) as ac:
        yield ac


@pytest.fixture
def mock_sentiment_analyzer() -> MagicMock:
    """Fixture for mocking the sentiment analyzer."""
    return MagicMock()


pytestmark = pytest.mark.asyncio


class TestSentimentEndpoint:
    async def test_analyze_sentiment_success(
        self,
        async_client: AsyncGenerator[AsyncClient, None],
        mock_sentiment_analyzer: MagicMock,
    ) -> None:
        """Test successful sentiment analysis."""
        async with async_client as client:  # type: ignore
            test_text = "This is a happy test message!"
            request = SentimentRequest(text=test_text)

            mock_sentiment_analyzer.analyze.return_value = {
                "polarity": 0.8,
                "subjectivity": 0.6,
            }

            response = await client.post("/api/v1/sentiment", json=request.model_dump())

            assert response.status_code == 200
            response_model = SentimentResponse.model_validate(response.json())
            assert response_model.scores == []
            assert response_model.text == test_text

    async def test_analyze_sentiment_invalid_text(
        self, async_client: AsyncGenerator[AsyncClient, None]
    ) -> None:
        """Test sentiment analysis with invalid text that's too long."""
        async with async_client as client:  # type: ignore
            # Create text that exceeds max length
            invalid_text = "x" * 5001  # Assuming 5000 is max length
            request = SentimentRequest(text=invalid_text)

            response = await client.post("/api/v1/sentiment", json=request.model_dump())

            assert response.status_code == 422
            error_detail = response.json()["detail"]
            assert any("text" in error["loc"] for error in error_detail)
