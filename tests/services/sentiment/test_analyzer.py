from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from sentiment_analyser.models.api.schema import EmotionScore, EmotionType
from sentiment_analyser.services.sentiment.analyzer import SentimentAnalyzer


@pytest.fixture
def mock_pipeline():
    with patch("sentiment_analyser.services.sentiment.analyzer.pipeline") as mock:
        pipeline_instance = Mock()
        mock.return_value = pipeline_instance
        yield pipeline_instance


@pytest.fixture
def analyzer(mock_pipeline: Mock):
    return SentimentAnalyzer(model_name="test-model")


# def test_analyzer_initialization(mock_pipeline: Mock):
#     """Test successful analyzer initialization."""
#     analyzer = SentimentAnalyzer(model_name="test-model")
#     assert analyzer.model_name == "test-model"
#     mock_pipeline.assert_called_once_with(
#         task="sentiment-analysis", model="test-model", device=-1
#     )


# def test_analyzer_initialization_failure(mock_pipeline: Mock):
#     """Test analyzer initialization failure."""
#     mock_pipeline.side_effect = Exception("Model loading failed")
#     with pytest.raises(ModelError) as exc_info:
#         SentimentAnalyzer(model_name="test-model")
#     assert str(exc_info.value) == "Model loading failed"


def test_analyze_text_success(analyzer: SentimentAnalyzer, mock_pipeline: Mock):
    """Test successful text analysis."""
    mock_pipeline.return_value = [
        {"label": "JOY", "score": 0.95},
        {"label": "SADNESS", "score": 0.05},
    ]

    result = analyzer.analyze_text("Test text")

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], EmotionScore)
    assert result[0].label == EmotionType.JOY
    assert result[0].score == 0.95


def test_analyze_text_invalid_output(analyzer: SentimentAnalyzer, mock_pipeline: Mock):
    """Test handling of invalid model output."""
    mock_pipeline.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        analyzer.analyze_text("Test text")
    assert exc_info.value.status_code == 500


def test_analyze_text_missing_fields(analyzer: SentimentAnalyzer, mock_pipeline: Mock):
    """Test handling of missing fields in model output."""
    mock_pipeline.return_value = [{"invalid": "format"}]

    with pytest.raises(HTTPException) as exc_info:
        analyzer.analyze_text("Test text")
    assert exc_info.value.status_code == 500


def test_analyzer_cleanup(analyzer: SentimentAnalyzer):
    """Test cleanup method."""
    analyzer.cleanup()
    assert not hasattr(analyzer, "model")


# @pytest.mark.asyncio
# async def test_analyzer_context_manager():
#     """Test async context manager."""
#     async with SentimentAnalyzer(model_name="test-model") as analyzer:
#         assert isinstance(analyzer, SentimentAnalyzer)
