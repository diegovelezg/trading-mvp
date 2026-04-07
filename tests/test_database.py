import os
import sqlite3
import pytest
import db_manager

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
