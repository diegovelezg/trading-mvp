import pytest
import os
from unittest.mock import MagicMock, patch
from trading_mvp.analysis.gemini_sentiment import analyze_sentiment

def test_analyze_sentiment_mocked():
    """Verify that analyze_sentiment calls Gemini API correctly and returns sentiment/summary."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
        with patch("trading_mvp.analysis.gemini_sentiment.Client") as MockClient:
            mock_client = MockClient.return_value
            
            # Mock Gemini response
            mock_response = MagicMock()
            mock_response.text = '{"sentiment": 0.8, "summary": "Great news!"}'
            
            # Configure mock to return the response
            mock_client.models.generate_content.return_value = mock_response
            
            # Call the function
            result = analyze_sentiment("Sample news content")
            
            # Verify results
            assert result["sentiment"] == 0.8
            assert result["summary"] == "Great news!"
            
            # Verify that the client was called
            mock_client.models.generate_content.assert_called_once()

def test_analyze_sentiment_markdown_json():
    """Verify that analyze_sentiment can handle markdown JSON blocks."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
        with patch("trading_mvp.analysis.gemini_sentiment.Client") as MockClient:
            mock_client = MockClient.return_value
            mock_response = MagicMock()
            mock_response.text = '```json\n{"sentiment": -0.5, "summary": "Bad news"}\n```'
            mock_client.models.generate_content.return_value = mock_response
            
            result = analyze_sentiment("Sample news")
            assert result["sentiment"] == -0.5
            assert result["summary"] == "Bad news"

def test_analyze_sentiment_exception():
    """Verify that analyze_sentiment handles exceptions gracefully."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
        with patch("trading_mvp.analysis.gemini_sentiment.Client") as MockClient:
            mock_client = MockClient.return_value
            mock_client.models.generate_content.side_effect = Exception("API error")
            
            result = analyze_sentiment("Sample news")
            assert result["sentiment"] == 0.0
            assert "Error: API error" in result["summary"]
