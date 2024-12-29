import pytest
from fastapi.testclient import TestClient
from sentiment_analyser.main import app, settings


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_health_check(client: TestClient):
    """
    Test the health check endpoint returns expected status and format
    """
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "version": settings.app.VERSION,
        "model_loaded": True,
        "model_name": None,
        "environment": "development",
    }
