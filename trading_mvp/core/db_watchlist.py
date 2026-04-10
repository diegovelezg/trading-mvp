"""Database schema and functions for watchlist management (PostgreSQL version)."""

import logging
import json
from typing import List, Dict, Optional
from trading_mvp.core.db_manager import get_connection
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

def create_watchlist_tables():
    """Create watchlist tables if they don't exist in PostgreSQL."""

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Main watchlist table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS watchlists (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    criteria_prompt TEXT,
                    criteria_summary TEXT,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Watchlist items (tickers)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS watchlist_items (
                    id SERIAL PRIMARY KEY,
                    watchlist_id INTEGER NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
                    ticker VARCHAR(10) NOT NULL,
                    company_name VARCHAR(255),
                    reason TEXT,
                    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (watchlist_id, ticker)
                );
            """)

            # Watchlist analysis results
            cur.execute("""
                CREATE TABLE IF NOT EXISTS watchlist_analysis (
                    id SERIAL PRIMARY KEY,
                    watchlist_id INTEGER NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
                    ticker VARCHAR(10) NOT NULL,

                    -- Analysis scores
                    geomacro_score FLOAT,
                    sentiment_score FLOAT,
                    risk_score FLOAT,

                    -- Metadata
                    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    data_sources JSONB,
                    UNIQUE (watchlist_id, ticker, analysis_date)
                );
            """)

            # Create indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_status ON watchlists(status);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_items_ticker ON watchlist_items(ticker);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_analysis_date ON watchlist_analysis(analysis_date DESC);")
            
            logger.info("✅ Watchlist tables created in Postgres")
    finally:
        conn.close()


def create_watchlist(name: str, description: str, criteria_prompt: str, criteria_summary: str = None) -> Optional[int]:
    """Create a new watchlist."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO watchlists (name, description, criteria_prompt, criteria_summary)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (name, description, criteria_prompt, criteria_summary))
            
            watchlist_id = cur.fetchone()[0]
            logger.info(f"✅ Created watchlist '{name}' with ID {watchlist_id}")
            return watchlist_id
    except Exception as e:
        logger.warning(f"⚠️  Could not create watchlist: {e}")
        return None
    finally:
        conn.close()


def add_ticker_to_watchlist(watchlist_id: int, ticker: str, company_name: str = None, reason: str = None) -> bool:
    """Add a ticker to a watchlist."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO watchlist_items (watchlist_id, ticker, company_name, reason)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (watchlist_id, ticker) DO NOTHING
            """, (watchlist_id, ticker.upper(), company_name, reason))
            
            logger.info(f"✅ Added {ticker} to watchlist {watchlist_id}")
            return True
    except Exception as e:
        logger.warning(f"⚠️  Could not add ticker: {e}")
        return False
    finally:
        conn.close()


def add_tickers_batch_to_watchlist(watchlist_id: int, tickers: List[Dict]) -> int:
    """Add multiple tickers to a watchlist."""
    added_count = 0
    for ticker_info in tickers:
        ticker = ticker_info.get('ticker', '').upper()
        company_name = ticker_info.get('company_name')
        reason = ticker_info.get('reason')
        if add_ticker_to_watchlist(watchlist_id, ticker, company_name, reason):
            added_count += 1
    return added_count


def get_watchlist(watchlist_id: int) -> Optional[Dict]:
    """Get watchlist details."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM watchlists WHERE id = %s", (watchlist_id,))
            return cur.fetchone()
    finally:
        conn.close()


def get_watchlist_tickers(watchlist_id: int) -> List[Dict]:
    """Get all tickers in a watchlist."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM watchlist_items
                WHERE watchlist_id = %s
                ORDER BY added_at DESC
            """, (watchlist_id,))
            return cur.fetchall()
    finally:
        conn.close()


def get_active_watchlists() -> List[Dict]:
    """Get all active watchlists."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM watchlists
                WHERE status = 'active'
                ORDER BY created_at DESC
            """)
            return cur.fetchall()
    finally:
        conn.close()


def save_watchlist_analysis(watchlist_id: int, ticker: str,
                            geomacro_score: float = None,
                            sentiment_score: float = None,
                            risk_score: float = None,
                            data_sources: List[str] = None) -> bool:
    """Save analysis results for a ticker in a watchlist."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sources_json = json.dumps(data_sources) if data_sources else None
            cur.execute("""
                INSERT INTO watchlist_analysis
                (watchlist_id, ticker, geomacro_score, sentiment_score, risk_score, data_sources)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (watchlist_id, ticker, analysis_date) DO UPDATE
                SET geomacro_score = EXCLUDED.geomacro_score,
                    sentiment_score = EXCLUDED.sentiment_score,
                    risk_score = EXCLUDED.risk_score,
                    data_sources = EXCLUDED.data_sources
            """, (watchlist_id, ticker.upper(), geomacro_score, sentiment_score, risk_score, sources_json))
            return True
    except Exception as e:
        logger.warning(f"⚠️  Could not save analysis: {e}")
        return False
    finally:
        conn.close()


def get_watchlist_analysis(watchlist_id: int, hours_back: int = 24) -> List[Dict]:
    """Get recent analysis for a watchlist."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM watchlist_analysis
                WHERE watchlist_id = %s
                AND analysis_date > (CURRENT_TIMESTAMP - INTERVAL '%s hours')
                ORDER BY analysis_date DESC
            """, (watchlist_id, hours_back))
            return cur.fetchall()
    finally:
        conn.close()
