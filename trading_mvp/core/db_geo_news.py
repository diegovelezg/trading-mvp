"""Database schema and functions for geo_macro_news table."""

import logging
import json
from typing import List, Dict, Optional
from trading_mvp.core.db_manager import get_connection

logger = logging.getLogger(__name__)

def create_geo_macro_news_table():
    """Create geo_macro_news table if it doesn't exist."""

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS geo_macro_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- News content
            title TEXT NOT NULL,
            summary TEXT,
            content TEXT,
            url TEXT,

            -- Source
            source TEXT,
            source_type TEXT,
            author TEXT,
            published_at TIMESTAMP,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            -- Source-specific IDs
            alpaca_id INTEGER,
            serpapi_position INTEGER,

            -- Raw data (JSON string for SQLite)
            raw_data TEXT,

            -- Prevent duplicates
            UNIQUE (source, alpaca_id)
        );
    """)

    # Create indexes
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_geo_news_source
        ON geo_macro_news(source);
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_geo_news_published
        ON geo_macro_news(published_at DESC);
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_geo_news_collected
        ON geo_macro_news(collected_at DESC);
    """)

    conn.commit()
    conn.close()

    logger.info("✅ geo_macro_news table created")


def insert_geo_news(news: Dict) -> Optional[int]:
    """Insert a single news item into geo_macro_news.

    Args:
        news: Normalized news item

    Returns:
        ID of inserted news, or None if failed
    """

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Convert raw_data dict to JSON string
        raw_data_str = json.dumps(news.get('raw_data', {})) if news.get('raw_data') else None

        cur.execute("""
            INSERT OR IGNORE INTO geo_macro_news (
                title, summary, content, url,
                source, source_type, author, published_at,
                alpaca_id, raw_data
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            news.get('title'),
            news.get('summary'),
            news.get('content'),
            news.get('url'),
            news.get('source'),
            news.get('source_type'),
            news.get('author'),
            news.get('published_at'),
            news.get('alpaca_id') or news.get('id'),
            raw_data_str
        ))

        conn.commit()

        # Get the inserted ID
        if cur.lastrowid:
            news_id = cur.lastrowid
        else:
            # If INSERT OR IGNORE was triggered, find existing ID
            cur.execute("""
                SELECT id FROM geo_macro_news
                WHERE source = ? AND alpaca_id = ?
            """, (news.get('source'), news.get('alpaca_id') or news.get('id')))
            result = cur.fetchone()
            news_id = result[0] if result else None

        conn.close()
        return news_id

    except Exception as e:
        logger.warning(f"⚠️  Could not insert news: {e}")
        conn.close()
        return None


def insert_geo_news_batch(news_list: List[Dict]) -> int:
    """Insert multiple news items into geo_macro_news.

    Args:
        news_list: List of normalized news items

    Returns:
        Number of news items inserted
    """

    inserted_count = 0

    for news in news_list:
        news_id = insert_geo_news(news)
        if news_id:
            inserted_count += 1

    logger.info(f"✅ Inserted {inserted_count}/{len(news_list)} news items")
    return inserted_count


def get_recent_news(hours_back: int = 24, limit: int = 100) -> List[Dict]:
    """Get recent news from database.

    Args:
        hours_back: Hours to look back
        limit: Maximum number of items

    Returns:
        List of news items
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM geo_macro_news
        WHERE collected_at > datetime('now', '-' || ? || ' hours')
        ORDER BY published_at DESC
        LIMIT ?
    """, (hours_back, limit))

    rows = cur.fetchall()

    # Convert to list of dicts
    columns = [desc[0] for desc in cur.description]
    news_list = []
    for row in rows:
        news_dict = dict(zip(columns, row))
        # Parse raw_data JSON string back to dict
        if news_dict.get('raw_data'):
            try:
                news_dict['raw_data'] = json.loads(news_dict['raw_data'])
            except:
                pass
        news_list.append(news_dict)

    conn.close()

    return news_list


def get_news_by_source(source: str, hours_back: int = 24, limit: int = 50) -> List[Dict]:
    """Get news from a specific source.

    Args:
        source: Source name ('alpaca_news', 'google_news', 'serpapi')
        hours_back: Hours to look back
        limit: Maximum number of items

    Returns:
        List of news items
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM geo_macro_news
        WHERE source = ?
        AND collected_at > datetime('now', '-' || ? || ' hours')
        ORDER BY published_at DESC
        LIMIT ?
    """, (source, hours_back, limit))

    rows = cur.fetchall()

    # Convert to list of dicts
    columns = [desc[0] for desc in cur.description]
    news_list = []
    for row in rows:
        news_dict = dict(zip(columns, row))
        # Parse raw_data JSON string back to dict
        if news_dict.get('raw_data'):
            try:
                news_dict['raw_data'] = json.loads(news_dict['raw_data'])
            except:
                pass
        news_list.append(news_dict)

    conn.close()

    return news_list


def get_news_count_by_source(hours_back: int = 24) -> Dict[str, int]:
    """Get count of news items by source.

    Args:
        hours_back: Hours to look back

    Returns:
        Dictionary with source names and counts
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT source, COUNT(*) as count
        FROM geo_macro_news
        WHERE collected_at > datetime('now', '-' || ? || ' hours')
        GROUP BY source
    """, (hours_back,))

    rows = cur.fetchall()
    counts = {row[0]: row[1] for row in rows if row[0]}

    conn.close()

    return counts
