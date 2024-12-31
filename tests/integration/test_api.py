import pytest


class TestHealthEndpoint:
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert data["model_loaded"] is True


class TestSentimentAnalysis:
    # def test_analyze_sentiment_success(
    #     self, client, api_headers, mock_sentiment_analyzer
    # ):
    #     """Test successful sentiment analysis."""
    #     response = client.post(
    #         "/api/v1/sentiment/analyze",
    #         json={"text": "I am very happy today!"},
    #         headers=api_headers,
    #     )

    #     assert response.status_code == 200
    #     data = response.json()
    #     assert data["text"] == "I am very happy today!"
    #     assert len(data["scores"]) == 2
    #     assert data["scores"][0]["label"] == "joy"
    #     assert data["scores"][0]["score"] == 0.95
    #     assert data["status"] == "success"

    @pytest.mark.parametrize(
        "test_input",
        [
            {"text": ""},  # Empty text
            {"text": "a" * 1001},  # Too long text
            {"text": None},  # None value
        ],
    )
    def test_analyze_sentiment_validation(self, client, api_headers, test_input):
        """Test input validation for sentiment analysis."""
        response = client.post(
            "/api/v1/sentiment/analyze", json=test_input, headers=api_headers
        )
        assert response.status_code == 422

    def test_analyze_sentiment_unauthorized(self, client):
        """Test authentication requirements."""
        # No API key
        response = client.post("/api/v1/sentiment/analyze", json={"text": "test"})
        assert response.status_code == 401

        # Invalid API key
        response = client.post(
            "/api/v1/sentiment/analyze",
            json={"text": "test"},
            headers={"x-api-key": "invalid-key"},
        )
        assert response.status_code == 401

    # class TestRateLimiting:
    #     @pytest.mark.parametrize(
    #         "endpoint", ["/api/v1/health", "/api/v1/sentiment/analyze"]
    #     )
    #     def test_rate_limiting(self, client, api_headers, endpoint):
    #         """Test rate limiting on endpoints."""
    #         settings = get_settings()
    #         limit = settings.rate_limit.DEFAULT_RATE_LIMIT

    #         # Make requests up to the limit
    #         for _ in range(limit):
    #             if endpoint == "/api/v1/sentiment/analyze":
    #                 response = client.post(
    #                     endpoint, json={"text": "test"}, headers=api_headers
    #                 )
    #             else:
    #                 response = client.get(endpoint)
    #             assert response.status_code != 429

    #         response = client.post(endpoint, json={"text": "test"}, headers=api_headers)
    #         assert response.status_code == 429
    # # Next request should be rate limited
    # if endpoint == "/api/v1/sentiment/analyze":
    #     response = client.post(
    #         endpoint, json={"text": "test"}, headers=api_headers
    #     )
    # else:
    #     response = client.get(endpoint)
    # assert response.status_code == 429

    def test_invalid_endpoint(self, client):
        """Test accessing an invalid endpoint."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
