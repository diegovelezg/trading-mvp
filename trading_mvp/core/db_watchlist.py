"""Database schema and functions for watchlist management."""

import logging
import json
from typing import List, Dict, Optional
from trading_mvp.core.db_manager import get_connection

logger = logging.getLogger(__name__)

def create_watchlist_tables():
    """Create watchlist tables if they don't exist."""

    conn = get_connection()
    cur = conn.cursor()

    # Main watchlist table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            criteria_prompt TEXT,
            criteria_summary TEXT,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Watchlist items (tickers)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS watchlist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            watchlist_id INTEGER NOT NULL,
            ticker VARCHAR(10) NOT NULL,
            company_name VARCHAR(255),
            reason TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (watchlist_id) REFERENCES watchlists(id) ON DELETE CASCADE,
            UNIQUE (watchlist_id, ticker)
        );
    """)

    # Watchlist analysis results
    cur.execute("""
        CREATE TABLE IF NOT EXISTS watchlist_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            watchlist_id INTEGER NOT NULL,
            ticker VARCHAR(10) NOT NULL,

            -- Analysis scores
            geomacro_score FLOAT,
            sentiment_score FLOAT,
            risk_score FLOAT,

            -- Metadata
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_sources TEXT,

            FOREIGN KEY (watchlist_id) REFERENCES watchlists(id) ON DELETE CASCADE,
            UNIQUE (watchlist_id, ticker, analysis_date)
        );
    """)

    # Create indexes
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_watchlist_status
        ON watchlists(status);
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_watchlist_items_ticker
        ON watchlist_items(ticker);
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_watchlist_analysis_date
        ON watchlist_analysis(analysis_date DESC);
    """)

    conn.commit()
    conn.close()

    logger.info("✅ Watchlist tables created")


def create_watchlist(name: str, description: str, criteria_prompt: str, criteria_summary: str = None) -> Optional[int]:
    """Create a new watchlist.

    Args:
        name: Watchlist name
        description: Description
        criteria_prompt: Original prompt used
        criteria_summary: Structured summary (optional)

    Returns:
        Watchlist ID, or None if failed
    """

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO watchlists (name, description, criteria_prompt, criteria_summary)
            VALUES (?, ?, ?, ?)
        """, (name, description, criteria_prompt, criteria_summary))

        watchlist_id = cur.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"✅ Created watchlist '{name}' with ID {watchlist_id}")
        return watchlist_id

    except Exception as e:
        logger.warning(f"⚠️  Could not create watchlist: {e}")
        conn.close()
        return None


def add_ticker_to_watchlist(watchlist_id: int, ticker: str, company_name: str = None, reason: str = None) -> bool:
    """Add a ticker to a watchlist.

    Args:
        watchlist_id: Watchlist ID
        ticker: Ticker symbol
        company_name: Company name (optional)
        reason: Reason for inclusion (optional)

    Returns:
        True if successful, False otherwise
    """

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT OR IGNORE INTO watchlist_items (watchlist_id, ticker, company_name, reason)
            VALUES (?, ?, ?, ?)
        """, (watchlist_id, ticker.upper(), company_name, reason))

        conn.commit()
        conn.close()

        logger.info(f"✅ Added {ticker} to watchlist {watchlist_id}")
        return True

    except Exception as e:
        logger.warning(f"⚠️  Could not add ticker: {e}")
        conn.close()
        return False


def add_tickers_batch_to_watchlist(watchlist_id: int, tickers: List[Dict]) -> int:
    """Add multiple tickers to a watchlist.

    Args:
        watchlist_id: Watchlist ID
        tickers: List of dicts with 'ticker', 'company_name', 'reason'

    Returns:
        Number of tickers added
    """

    added_count = 0

    for ticker_info in tickers:
        ticker = ticker_info.get('ticker', '').upper()
        company_name = ticker_info.get('company_name')
        reason = ticker_info.get('reason')

        if add_ticker_to_watchlist(watchlist_id, ticker, company_name, reason):
            added_count += 1

    logger.info(f"✅ Added {added_count}/{len(tickers)} tickers to watchlist {watchlist_id}")
    return added_count


def get_watchlist(watchlist_id: int) -> Optional[Dict]:
    """Get watchlist details.

    Args:
        watchlist_id: Watchlist ID

    Returns:
        Watchlist dict, or None if not found
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM watchlists WHERE id = ?
    """, (watchlist_id,))

    row = cur.fetchone()

    if row:
        columns = [desc[0] for desc in cur.description]
        watchlist = dict(zip(columns, row))
    else:
        watchlist = None

    conn.close()
    return watchlist


def get_watchlist_tickers(watchlist_id: int) -> List[Dict]:
    """Get all tickers in a watchlist.

    Args:
        watchlist_id: Watchlist ID

    Returns:
        List of ticker dicts
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM watchlist_items
        WHERE watchlist_id = ?
        ORDER BY added_at DESC
    """, (watchlist_id,))

    rows = cur.fetchall()

    columns = [desc[0] for desc in cur.description]
    tickers = [dict(zip(columns, row)) for row in rows]

    conn.close()
    return tickers


def get_active_watchlists() -> List[Dict]:
    """Get all active watchlists.

    Returns:
        List of watchlist dicts
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM watchlists
        WHERE status = 'active'
        ORDER BY created_at DESC
    """)

    rows = cur.fetchall()

    columns = [desc[0] for desc in cur.description]
    watchlists = [dict(zip(columns, row)) for row in rows]

    conn.close()
    return watchlists


def save_watchlist_analysis(watchlist_id: int, ticker: str,
                            geomacro_score: float = None,
                            sentiment_score: float = None,
                            risk_score: float = None,
                            data_sources: List[str] = None) -> bool:
    """Save analysis results for a ticker in a watchlist.

    Args:
        watchlist_id: Watchlist ID
        ticker: Ticker symbol
        geomacro_score: GeoMacro impact score
        sentiment_score: Sentiment score
        risk_score: Risk score
        data_sources: List of agents that contributed

    Returns:
        True if successful, False otherwise
    """

    conn = get_connection()
    cur = conn.cursor()

    try:
        sources_json = json.dumps(data_sources) if data_sources else None

        cur.execute("""
            INSERT OR REPLACE INTO watchlist_analysis
            (watchlist_id, ticker, geomacro_score, sentiment_score, risk_score, data_sources)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (watchlist_id, ticker.upper(), geomacro_score, sentiment_score, risk_score, sources_json))

        conn.commit()
        conn.close()

        logger.info(f"✅ Saved analysis for {ticker} in watchlist {watchlist_id}")
        return True

    except Exception as e:
        logger.warning(f"⚠️  Could not save analysis: {e}")
        conn.close()
        return False


def get_watchlist_analysis(watchlist_id: int, hours_back: int = 24) -> List[Dict]:
    """Get recent analysis for a watchlist.

    Args:
        watchlist_id: Watchlist ID
        hours_back: Hours to look back

    Returns:
        List of analysis dicts
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM watchlist_analysis
        WHERE watchlist_id = ?
        AND analysis_date > datetime('now', '-' || ? || ' hours')
        ORDER BY analysis_date DESC
    """, (watchlist_id, hours_back))

    rows = cur.fetchall()

    columns = [desc[0] for desc in cur.description]
    analysis = []
    for row in rows:
        analysis_dict = dict(zip(columns, row))
        # Parse data_sources JSON
        if analysis_dict.get('data_sources'):
            try:
                analysis_dict['data_sources'] = json.loads(analysis_dict['data_sources'])
            except:
                analysis_dict['data_sources'] = []
        analysis.append(analysis_dict)

    conn.close()
    return analysis
