import os
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from sentiment_analyser.main import app


@pytest.fixture(autouse=True)
def test_env():
    """Set test environment and load test config."""
    os.environ["ENVIRONMENT"] = "testing"

    # Ensure test env file exists
    test_env_file = Path(__file__).parent.parent / ".env.testing"
    if not test_env_file.exists():
        raise FileNotFoundError(f"Test environment file not found: {test_env_file}")

    yield
    os.environ.pop("ENVIRONMENT", None)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_settings():
    """Override settings for testing."""
    from sentiment_analyser.core.settings import get_settings

    settings = get_settings()
    original_model = settings.model.MODEL_NAME
    settings.model.MODEL_NAME = "test-model"
    yield settings
    settings.model.MODEL_NAME = original_model


@pytest.fixture
def mock_model():
    """Mock transformer model for testing."""
    with patch("transformers.pipeline") as mock:
        yield mock


@pytest.fixture
def headers():
    """Default headers for API requests."""
    return {"Content-Type": "application/json", "Accept": "application/json"}


@pytest.fixture
def api_key():
    """Default API key for testing."""
    return "dev-key-1"


@pytest.fixture
def api_headers(api_key):
    """Default headers for API requests."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-api-key": api_key,
    }


@pytest.fixture
def mock_sentiment_analyzer():
    """Mock sentiment analyzer for testing."""
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
