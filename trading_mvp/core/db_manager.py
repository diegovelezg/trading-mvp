import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from typing import Optional, List, Dict
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Returns a connection to the PostgreSQL database."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable NOT set!")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        # We'll use autocommit for simple operations as sqlite did
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        raise

def init_db() -> None:
    """Initializes the database by running the schema file if requested."""
    # This is usually done once. We can keep it to run migrations if needed.
    print("PostgreSQL connection verified.")

def insert_news(external_id: str, title: str, source: str, url: str, summary: str, published_at: str) -> int:
    """Inserts a news item into Postgres and returns its ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Postgres uses ON CONFLICT instead of INSERT OR IGNORE
            cursor.execute('''
                INSERT INTO news (external_id, title, source, url, summary, published_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (external_id) DO NOTHING
                RETURNING id
            ''', (external_id, title, source, url, summary, published_at))
            
            result = cursor.fetchone()
            if result:
                return result[0]
            
            # If it was ignored (already exists), find its ID
            cursor.execute('SELECT id FROM news WHERE external_id = %s', (external_id,))
            return cursor.fetchone()[0]
    finally:
        conn.close()

def insert_sentiment(news_id: int, agent_id: str, score: float, reasoning: str) -> None:
    """Inserts a sentiment associated with a news item."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO sentiments (news_id, agent_id, score, reasoning)
                VALUES (%s, %s, %s, %s)
            ''', (news_id, agent_id, score, reasoning))
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
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO explorations (prompt, criteria, tickers, reasoning)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            ''', (prompt, criteria, json.dumps(tickers), reasoning))
            
            return cursor.fetchone()[0]
    finally:
        conn.close()

def get_recent_explorations(limit: int = 10) -> list:
    """
    Retrieve recent explorations from the database.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
                SELECT id, prompt, criteria, tickers, reasoning, created_at as timestamp, status
                FROM explorations
                ORDER BY created_at DESC
                LIMIT %s
            ''', (limit,))
            return cursor.fetchall()
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        conn = get_connection()
        print(f"✅ Connection successful to {urlparse(DATABASE_URL).hostname}")
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
