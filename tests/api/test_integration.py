from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_sentiment_analyzer():
    with patch(
        "sentiment_analyser.services.sentiment.service.SentimentAnalyzer"
    ) as mock:
        instance = mock.return_value
        instance.__aenter__.return_value = instance
        instance.analyze_text.return_value = [
            {"label": "joy", "score": 0.95},
            {"label": "sadness", "score": 0.05},
        ]
        yield instance


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["model_loaded"] is True


# def test_analyze_sentiment_success(client: TestClient, mock_sentiment_analyzer):
#     """Test successful sentiment analysis."""
#     response = client.post(
#         "/api/v1/sentiment/analyze", json={"text": "I am very happy today!"}
#     )

#     assert response.status_code == 200
#     data = response.json()
#     assert data["text"] == "I am very happy today!"
#     assert len(data["scores"]) == 2
#     assert data["scores"][0]["label"] == "joy"
#     assert data["scores"][0]["score"] == 0.95
#     assert data["status"] == "success"


def test_analyze_no_api_key(client: TestClient):
    """Test sentiment analysis with empty text."""
    response = client.post(
        "/api/v1/sentiment/analyze",
        json={"text": "test"},
    )

    assert response.status_code == 500


def test_analyze_bad_api_key(client: TestClient):
    """Test sentiment analysis with empty text."""
    response = client.post(
        "/api/v1/sentiment/analyze",
        json={"text": "test"},
        headers={"x-api-key": "dev-key-11"},
    )

    assert response.status_code == 500


def test_analyze_sentiment_empty_text(client: TestClient):
    """Test sentiment analysis with empty text."""
    response = client.post(
        "/api/v1/sentiment/analyze",
        json={"text": ""},
        headers={"x-api-key": "dev-key-1"},
    )
    print(response.json())
    assert response.status_code == 422


def test_analyze_sentiment_long_text(client: TestClient):
    """Test sentiment analysis with text exceeding max length."""
    response = client.post(
        "/api/v1/sentiment/analyze",
        headers={"x-api-key": "dev-key-1"},
        json={"text": "a" * 1001},  # Exceeds max_length=1000
    )

    assert response.status_code == 422


def test_analyze_sentiment_invalid_json(client: TestClient):
    """Test sentiment analysis with invalid JSON."""
    response = client.post(
        "/api/v1/sentiment/analyze",
        headers={"x-api-key": "dev-key-1"},
        content="invalid json",
    )

    assert response.status_code == 422


# @pytest.mark.parametrize("endpoint", ["/api/v1/health", "/api/v1/sentiment/analyze"])
# def test_rate_limiting(client: TestClient, endpoint):
#     """Test rate limiting on endpoints."""
#     settings = get_settings()
#     limit = settings.rate_limit.DEFAULT_RATE_LIMIT

#     # Make requests up to the limit
#     for _ in range(limit):
#         if endpoint == "/api/v1/sentiment/analyze":
#             response = client.post(endpoint, json={"text": "test"})
#         else:
#             response = client.get(endpoint)
#         assert response.status_code != 429

#     # Next request should be rate limited
#     if endpoint == "/api/v1/sentiment/analyze":
#         response = client.post(endpoint, json={"text": "test"})
#     else:
#         response = client.get(endpoint)
#     assert response.status_code == 429


def test_invalid_endpoint(client: TestClient):
    """Test accessing an invalid endpoint."""
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
