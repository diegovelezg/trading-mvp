import sqlite3
import pytest
from src.core import db_manager

def test_explorations_table_exists():
    """Verify that the explorations table exists in the database."""
    db_manager.init_db()
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='explorations'")
    assert cursor.fetchone() is not None
    conn.close()

def test_insert_exploration():
    """Verify that an exploration can be inserted and retrieved."""
    prompt = "Test thematic prompt"
    results = '["TICK1", "TICK2"]'
    
    # This should fail if insert_exploration is not yet implemented
    exploration_id = db_manager.insert_exploration(prompt, results)
    
    assert isinstance(exploration_id, int)
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT prompt, results FROM explorations WHERE id = ?", (exploration_id,))
    row = cursor.fetchone()
    assert row[0] == prompt
    assert row[1] == results
    conn.close()
