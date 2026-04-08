import sqlite3
import os
from typing import Optional

# Get the project root directory (3 levels up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "trading.db")

def get_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db() -> None:
    """Initializes the database and creates required tables."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Create news table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT UNIQUE,
                title TEXT NOT NULL,
                source TEXT,
                url TEXT,
                summary TEXT,
                published_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create sentiments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id INTEGER,
                agent_id TEXT,
                score REAL,
                reasoning TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (news_id) REFERENCES news (id)
            )
        ''')

        # Create tickers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT,
                sector TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                qty INTEGER,
                price REAL,
                side TEXT,
                status TEXT,
                filled_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create explorations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS explorations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                results TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
    finally:
        conn.close()

def insert_news(external_id: str, title: str, source: str, url: str, summary: str, published_at: str) -> int:
    """Inserts a news item into the database and returns its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO news (external_id, title, source, url, summary, published_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (external_id, title, source, url, summary, published_at))
        
        # If it was ignored (already exists), find its ID
        if cursor.rowcount == 0:
            cursor.execute('SELECT id FROM news WHERE external_id = ?', (external_id,))
            news_id = cursor.fetchone()[0]
        else:
            news_id = cursor.lastrowid
            
        conn.commit()
        return news_id
    finally:
        conn.close()

def insert_sentiment(news_id: int, agent_id: str, score: float, reasoning: str) -> None:
    """Inserts a sentiment associated with a news item."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO sentiments (news_id, agent_id, score, reasoning)
            VALUES (?, ?, ?, ?)
        ''', (news_id, agent_id, score, reasoning))
        conn.commit()
    finally:
        conn.close()

def insert_exploration(prompt: str, criteria: str, tickers: list, reasoning: str = "") -> int:
    """
    Inserts an exploration result into the database with full context.

    Args:
        prompt: The thematic prompt used for discovery
        criteria: The search criteria applied
        tickers: List of discovered ticker symbols
        reasoning: AI reasoning for the selection

    Returns:
        exploration_id: The ID of the inserted exploration
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        import json
        cursor.execute('''
            INSERT INTO explorations (prompt, criteria, tickers, reasoning)
            VALUES (?, ?, ?, ?)
        ''', (prompt, criteria, json.dumps(tickers), reasoning))

        exploration_id = cursor.lastrowid
        conn.commit()
        return exploration_id
    finally:
        conn.close()

def get_recent_explorations(limit: int = 10) -> list:
    """
    Retrieve recent explorations from the database.

    Args:
        limit: Maximum number of explorations to return

    Returns:
        List of exploration records
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT id, prompt, criteria, tickers, reasoning, timestamp, status
            FROM explorations
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        explorations = []
        for row in cursor.fetchall():
            explorations.append({
                'id': row[0],
                'prompt': row[1],
                'criteria': row[2],
                'tickers': row[3],
                'reasoning': row[4],
                'timestamp': row[5],
                'status': row[6]
            })
        return explorations
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
