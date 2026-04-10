"""Database schema and functions for geo_macro_news table."""

import logging
import json
from typing import List, Dict, Optional
from trading_mvp.core.db_manager import get_connection
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

def create_geo_macro_news_table():
    """Create geo_macro_news table if it doesn't exist."""

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS geo_macro_news (
                id SERIAL PRIMARY KEY,

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

                -- Raw data (JSONB for Postgres)
                raw_data JSONB,

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
    try:
        with conn.cursor() as cur:
            # raw_data is JSONB in Postgres, we use json.dumps() before insertion
            raw_data_json = json.dumps(news.get('raw_data', {})) if news.get('raw_data') else None

            cur.execute("""
                INSERT INTO geo_macro_news (
                    title, summary, content, url,
                    source, source_type, author, published_at,
                    alpaca_id, raw_data
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (source, alpaca_id) DO NOTHING
                RETURNING id
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
                raw_data_json
            ))

            result = cur.fetchone()
            if result:
                news_id = result[0]
            else:
                # If ON CONFLICT DO NOTHING was triggered, find existing ID
                cur.execute("""
                    SELECT id FROM geo_macro_news
                    WHERE source = %s AND alpaca_id = %s
                """, (news.get('source'), news.get('alpaca_id') or news.get('id')))
                result = cur.fetchone()
                news_id = result[0] if result else None

            conn.commit()
            return news_id

    except Exception as e:
        logger.warning(f"⚠️  Could not insert news: {e}")
        return None
    finally:
        conn.close()


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
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM geo_macro_news
                WHERE collected_at > CURRENT_TIMESTAMP - (INTERVAL '1 hour' * %s)
                ORDER BY published_at DESC
                LIMIT %s
            """, (hours_back, limit))

            rows = cur.fetchall()
            # Convert RealDictRow to regular dict
            return [dict(row) for row in rows]
    finally:
        conn.close()


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
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM geo_macro_news
                WHERE source = %s
                AND collected_at > CURRENT_TIMESTAMP - (INTERVAL '1 hour' * %s)
                ORDER BY published_at DESC
                LIMIT %s
            """, (source, hours_back, limit))

            rows = cur.fetchall()
            return [dict(row) for row in rows]
    finally:
        conn.close()


def get_news_count_by_source(hours_back: int = 24) -> Dict[str, int]:
    """Get count of news items by source.

    Args:
        hours_back: Hours to look back

    Returns:
        Dictionary with source names and counts
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT source, COUNT(*) as count
                FROM geo_macro_news
                WHERE collected_at > CURRENT_TIMESTAMP - (INTERVAL '1 hour' * %s)
                GROUP BY source
            """, (hours_back,))

            rows = cur.fetchall()
            counts = {row[0]: row[1] for row in rows if row[0]}
            return counts
    finally:
        conn.close()
