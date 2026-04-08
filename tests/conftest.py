"""Shared fixtures and configuration for pytest tests."""

import os
import sys
import tempfile
import pytest
from unittest.mock import MagicMock, patch

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Also add .claude to path
sys.path.insert(0, os.path.join(project_root, ".claude"))

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def mock_env_vars():
    """Provide mock environment variables for APIs."""
    return {
        "ALPACA_API_KEY_ID": "test_alpaca_key",
        "ALPACA_API_SECRET_KEY": "test_alpaca_secret",
        "GEMINI_API_KEY": "test_gemini_key",
    }


@pytest.fixture
def mock_news_item():
    """Provide a mock news item for testing."""
    return {
        "external_id": "test_news_123",
        "title": "Test News Title",
        "author": "Test Author",
        "content": "Test news content for analysis",
        "url": "https://example.com/news/123",
        "created_at": "2026-04-08T12:00:00Z"
    }


@pytest.fixture
def mock_sentiment_result():
    """Provide a mock sentiment analysis result."""
    return {
        "sentiment": 0.75,
        "summary": "Positive sentiment detected in the news"
    }


@pytest.fixture
def mock_ticker_list():
    """Provide a mock list of tickers."""
    return ["AAPL", "MSFT", "GOOGL", "TSLA"]


@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test to ensure isolation."""
    # This will automatically run before each test
    yield
    # Cleanup after test if needed
    pass


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
