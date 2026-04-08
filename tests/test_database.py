import os
import sqlite3
import pytest
from src.core import db_manager

DB_PATH = "trading.db"

def test_database_tables():
    """Verify that the required tables exist in the database."""
    # Ensure DB is initialized
    db_manager.init_db()
    
    if not os.path.exists(DB_PATH):
        pytest.fail(f"Database file {DB_PATH} does not exist")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check for required tables
    required_tables = ["news", "sentiments", "tickers", "trades"]
    for table in required_tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        assert cursor.fetchone() is not None, f"Table {table} is missing"
    
    conn.close()

def test_insert_news_and_sentiment():
    """Verify that news and sentiments can be inserted and retrieved."""
    # Ensure DB is initialized
    db_manager.init_db()
    
    # Insert a news item
    news_id = db_manager.insert_news(
        external_id="test_id_123",
        title="Test News Title",
        source="Test Source",
        url="http://example.com/test",
        summary="Test Summary",
        published_at="2026-04-07T12:00:00Z"
    )
    
    assert isinstance(news_id, int)
    
    # Insert a sentiment
    db_manager.insert_sentiment(
        news_id=news_id,
        agent_id="test_agent",
        score=0.75,
        reasoning="Positive news"
    )
    
    # Verify retrieval
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM news WHERE id = ?', (news_id,))
    news_row = cursor.fetchone()
    assert news_row is not None
    assert news_row[1] == "test_id_123"
    
    cursor.execute('SELECT * FROM sentiments WHERE news_id = ?', (news_id,))
    sentiment_row = cursor.fetchone()
    assert sentiment_row is not None
    assert sentiment_row[3] == 0.75
    
    conn.close()
