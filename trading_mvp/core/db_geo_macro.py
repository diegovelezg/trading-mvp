"""GeoMacro Database Schema and Operations."""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from trading_mvp.core.db_manager import get_connection
from psycopg2.extras import RealDictCursor

def create_geo_macro_tables():
    """Create GeoMacro insights database schema."""
    conn = get_connection()
    with conn.cursor() as cursor:
        # Main insights table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS geo_macro_insights (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                importance TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                impact_analysis TEXT NOT NULL,
                affected_sectors JSONB,
                affected_regions JSONB,
                affected_tickers JSONB,
                time_horizon TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                sources JSONB,
                tags JSONB,
                raw_data TEXT,
                session_type TEXT,  -- morning, afternoon, ad-hoc
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes for efficient querying
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_geo_macro_timestamp
            ON geo_macro_insights(timestamp DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_geo_macro_importance
            ON geo_macro_insights(importance)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_geo_macro_event_type
            ON geo_macro_insights(event_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_geo_macro_tickers
            ON geo_macro_insights(affected_tickers)
        """)

    conn.commit()
    conn.close()
    print("✅ GeoMacro database schema created")

def insert_geo_macro_insight(insight: Dict) -> int:
    """Insert a new geo-macro insight into database.

    Args:
        insight: Dictionary containing all insight fields

    Returns:
        ID of inserted insight
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO geo_macro_insights (
                    event_type, importance, title, summary, impact_analysis,
                    affected_sectors, affected_regions, affected_tickers,
                    time_horizon, confidence_score, sources, tags, raw_data, session_type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                insight['event_type'],
                insight['importance'],
                insight['title'],
                insight['summary'],
                insight['impact_analysis'],
                json.dumps(insight.get('affected_sectors', [])),
                json.dumps(insight.get('affected_regions', [])),
                json.dumps(insight.get('affected_tickers', [])),
                insight['time_horizon'],
                insight['confidence_score'],
                json.dumps(insight.get('sources', [])),
                json.dumps(insight.get('tags', [])),
                insight.get('raw_data', ''),
                insight.get('session_type', 'ad-hoc')
            ))

            insight_id = cursor.fetchone()[0]
            conn.commit()
            return insight_id
    finally:
        conn.close()

def get_recent_insights(hours: int = 48, min_importance: str = "medium") -> List[Dict]:
    """Get recent geo-macro insights.

    Args:
        hours: Hours to look back (default: 48)
        min_importance: Minimum importance level (low, medium, high, critical)

    Returns:
        List of insight dictionaries
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            importance_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            min_score = importance_order.get(min_importance, 0)

            cursor.execute("""
                SELECT * FROM geo_macro_insights
                WHERE timestamp > CURRENT_TIMESTAMP - (INTERVAL '1 hour' * %s)
                ORDER BY
                    CASE importance
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                    END,
                    timestamp DESC
            """, (hours,))

            rows = cursor.fetchall()
            insights = [_process_row(row) for row in rows]
            
            # Filter by minimum importance
            filtered = [i for i in insights if importance_order.get(i['importance'], 0) >= min_score]
            return filtered
    finally:
        conn.close()

def get_insights_for_ticker(ticker: str, hours: int = 72) -> List[Dict]:
    """Get insights relevant to a specific ticker.

    Args:
        ticker: Ticker symbol
        hours: Hours to look back (default: 72)

    Returns:
        List of relevant insights
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Note: Using casts to text for ILIKE on JSONB if needed, or better use JSONB operators.
            # For simplicity, if tickers is a JSON array of strings, we can use:
            # affected_tickers @> '["TICKER"]'
            # But the user might want a partial match or the old behavior.
            # SQLite's affected_tickers was TEXT containing JSON.
            # Postgres JSONB column can be queried with @>
            ticker_json = json.dumps([ticker])
            cursor.execute("""
                SELECT * FROM geo_macro_insights
                WHERE (affected_tickers @> %s::jsonb OR title ILIKE %s OR summary ILIKE %s)
                AND timestamp > CURRENT_TIMESTAMP - (INTERVAL '1 hour' * %s)
                ORDER BY timestamp DESC
            """, (ticker_json, f"%{ticker}%", f"%{ticker}%", hours))

            rows = cursor.fetchall()
            return [_process_row(row) for row in rows]
    finally:
        conn.close()

def get_insights_for_sector(sector: str, hours: int = 72) -> List[Dict]:
    """Get insights relevant to a specific sector.

    Args:
        sector: Sector name
        hours: Hours to look back (default: 72)

    Returns:
        List of relevant insights
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            sector_json = json.dumps([sector])
            cursor.execute("""
                SELECT * FROM geo_macro_insights
                WHERE (affected_sectors @> %s::jsonb OR summary ILIKE %s)
                AND timestamp > CURRENT_TIMESTAMP - (INTERVAL '1 hour' * %s)
                ORDER BY timestamp DESC
            """, (sector_json, f"%{sector}%", hours))

            rows = cursor.fetchall()
            return [_process_row(row) for row in rows]
    finally:
        conn.close()

def get_insights_for_region(region: str, hours: int = 72) -> List[Dict]:
    """Get insights relevant to a specific region.

    Args:
        region: Region name (country, continent, etc.)
        hours: Hours to look back (default: 72)

    Returns:
        List of relevant insights
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            region_json = json.dumps([region])
            cursor.execute("""
                SELECT * FROM geo_macro_insights
                WHERE (affected_regions @> %s::jsonb OR summary ILIKE %s)
                AND timestamp > CURRENT_TIMESTAMP - (INTERVAL '1 hour' * %s)
                ORDER BY timestamp DESC
            """, (region_json, f"%{region}%", hours))

            rows = cursor.fetchall()
            return [_process_row(row) for row in rows]
    finally:
        conn.close()

def get_critical_insights(hours: int = 24) -> List[Dict]:
    """Get only critical/high importance insights.

    Args:
        hours: Hours to look back (default: 24)

    Returns:
        List of critical insights
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM geo_macro_insights
                WHERE importance IN ('critical', 'high')
                AND timestamp > CURRENT_TIMESTAMP - (INTERVAL '1 hour' * %s)
                ORDER BY
                    CASE importance
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                    END,
                    timestamp DESC
            """, (hours,))

            rows = cursor.fetchall()
            return [_process_row(row) for row in rows]
    finally:
        conn.close()

def _process_row(row) -> Dict:
    """Process database row (RealDictRow) to ensure JSON fields are parsed if necessary.
    Psycopg2 with JSONB usually returns them as dicts/lists already.
    """
    d = dict(row)
    # If using JSONB, these might already be lists/dicts. 
    # If they are still strings (unlikely with JSONB but possible if type was TEXT), we'd parse them.
    for field in ['affected_sectors', 'affected_regions', 'affected_tickers', 'sources', 'tags']:
        if isinstance(d.get(field), str):
            try:
                d[field] = json.loads(d[field])
            except:
                d[field] = []
    return d

def get_insight_summary(hours: int = 24) -> Dict:
    """Get summary of recent insights.

    Args:
        hours: Hours to look back (default: 24)

    Returns:
        Summary dictionary with counts and highlights
    """
    insights = get_recent_insights(hours=hours)

    summary = {
        'total_insights': len(insights),
        'by_importance': {},
        'by_event_type': {},
        'critical_insights': [],
        'high_insights': []
    }

    for insight in insights:
        # Count by importance
        imp = insight['importance']
        summary['by_importance'][imp] = summary['by_importance'].get(imp, 0) + 1

        # Count by event type
        event_type = insight['event_type']
        summary['by_event_type'][event_type] = summary['by_event_type'].get(event_type, 0) + 1

        # Collect critical and high insights
        if imp == 'critical':
            summary['critical_insights'].append(insight)
        elif imp == 'high':
            summary['high_insights'].append(insight)

    return summary
