from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from sentiment_analyser.main import app


@pytest.fixture(autouse=True)
def test_env():
    """Set test environment."""
    import os

    os.environ["ENVIRONMENT"] = "test"
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
