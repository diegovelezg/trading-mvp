import pytest
from unittest.mock import MagicMock, patch
from src.agents.macro_analyst import ingest_and_analyze

def test_ingest_and_analyze_flow():
    """Verify the integrated flow: fetch news -> analyze sentiment -> store in DB."""
    with patch("src.agents.macro_analyst.fetch_news") as mock_fetch:
        with patch("src.agents.macro_analyst.analyze_sentiment") as mock_analyze:
            with patch("src.agents.macro_analyst.insert_news") as mock_insert_news:
                with patch("src.agents.macro_analyst.insert_sentiment") as mock_insert_sentiment:
                    
                    # Mock data
                    mock_fetch.return_value = [{
                        "external_id": "ext1",
                        "title": "Stock Up",
                        "author": "Author 1",
                        "content": "Stocks are doing great.",
                        "url": "http://example.com/1",
                        "created_at": "2026-04-07T12:00:00Z"
                    }]
                    
                    mock_analyze.return_value = {
                        "sentiment": 0.9,
                        "summary": "Bullish news."
                    }
                    
                    mock_insert_news.return_value = 1  # news_id
                    
                    # Call function
                    ingest_and_analyze(symbols=["AAPL"])
                    
                    # Verify flow
                    mock_fetch.assert_called_once_with(symbols=["AAPL"])
                    mock_analyze.assert_called_once_with("Stocks are doing great.")
                    mock_insert_news.assert_called_once()
                    mock_insert_sentiment.assert_called_once()
