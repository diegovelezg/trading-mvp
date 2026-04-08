import pytest
import os
from unittest.mock import MagicMock, patch
from explorer_agent import discover_tickers

def test_discover_tickers_mocked():
    """Verify that discover_tickers calls Gemini API correctly and returns a list of symbols."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
        with patch("explorer_agent.Client") as MockClient:
            with patch("explorer_agent.insert_exploration") as mock_insert:
                mock_client = MockClient.return_value
                
                # Mock Gemini response
                mock_response = MagicMock()
                mock_response.text = '{"tickers": ["AAPL", "MSFT", "GOOGL"], "reasoning": "Major tech companies"}'
                
                # Configure mock to return the response
                mock_client.models.generate_content.return_value = mock_response
                
                # Call the function
                tickers = discover_tickers("large tech companies")
                
                # Verify results
                assert tickers == ["AAPL", "MSFT", "GOOGL"]
                
                # Verify that the client was called
                mock_client.models.generate_content.assert_called_once()
                mock_insert.assert_called_once()

def test_explorer_cli():
    """Verify that explorer_agent.py can be run from CLI with a prompt."""
    with patch("sys.argv", ["explorer_agent.py", "tech companies"]):
        with patch("explorer_agent.discover_tickers") as mock_discover:
            mock_discover.return_value = ["AAPL", "MSFT"]
            import explorer_agent
            explorer_agent.main()
            mock_discover.assert_called_once_with("tech companies")

def test_discover_tickers_thematic_structure():
    """Verify that discover_tickers returns a list of strings for various themes."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
        with patch("explorer_agent.Client") as MockClient:
            with patch("explorer_agent.insert_exploration"):
                mock_client = MockClient.return_value
                mock_response = MagicMock()
                mock_response.text = '{"tickers": ["T1", "T2"], "reasoning": "test"}'
                mock_client.models.generate_content.return_value = mock_response
                
                themes = ["energy", "ai", "biotech"]
                for theme in themes:
                    tickers = discover_tickers(theme)
                    assert isinstance(tickers, list)
                    assert all(isinstance(t, str) for t in tickers)

def test_discover_tickers_markdown_json():
    """Verify that discover_tickers handles markdown JSON blocks."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
        with patch("explorer_agent.Client") as MockClient:
            with patch("explorer_agent.insert_exploration") as mock_insert:
                mock_client = MockClient.return_value
                mock_response = MagicMock()
                mock_response.text = '```json\n{"tickers": ["X", "Y"], "reasoning": "Markdown test"}\n```'
                mock_client.models.generate_content.return_value = mock_response
                
                tickers = discover_tickers("test markdown")
                assert tickers == ["X", "Y"]
                mock_insert.assert_called_once()

def test_discover_tickers_exception():
    """Verify that discover_tickers handles exceptions gracefully."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
        with patch("explorer_agent.Client") as MockClient:
            mock_client = MockClient.return_value
            mock_client.models.generate_content.side_effect = Exception("Discovery failed")
            
            tickers = discover_tickers("test exception")
            assert tickers == []
