import pytest
import os
from unittest.mock import MagicMock, patch
from alpaca_news import fetch_news

def test_fetch_news_mocked():
    """Verify that fetch_news calls the Alpaca API correctly."""
    with patch.dict(os.environ, {"ALPACA_API_KEY_ID": "fake_key", "ALPACA_API_SECRET_KEY": "fake_secret"}):
        with patch("alpaca_news.NewsClient") as MockClient:
            mock_client = MockClient.return_value
            # Mock the news response
            mock_news = MagicMock()
            mock_news.title = "Test News"
            mock_news.author = "Test Author"
            mock_news.content = "Test Content"
            mock_news.url = "http://test.com"
            mock_news.id = "123"
            mock_news.created_at = "2026-04-07T12:00:00Z"
            
            # Configure the mock to return a list with one news item
            mock_client.get_news.return_value = MagicMock(news=[mock_news])
            
            # Call the function
            news_items = fetch_news(symbols=["AAPL"])
            
            # Verify the results
            assert len(news_items) == 1
            assert news_items[0]["title"] == "Test News"
            assert news_items[0]["external_id"] == "123"
            
            # Verify that the client was called correctly
            mock_client.get_news.assert_called_once()
