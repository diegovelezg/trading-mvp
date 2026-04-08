"""Database schema for geo_macro_entities table."""

import logging
import json
from typing import List, Dict, Optional
from trading_mvp.core.db_manager import get_connection

logger = logging.getLogger(__name__)

def create_geo_macro_entities_table():
    """Create geo_macro_entities table if it doesn't exist."""

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS geo_macro_entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Relation to news
            news_id INTEGER NOT NULL,

            -- Entity information
            entity_name VARCHAR(255) NOT NULL,
            entity_type VARCHAR(50),    -- 'theme', 'commodity', 'region', 'event', 'policy', 'sector', 'indicator'
            impact VARCHAR(20),          -- 'positive', 'negative', 'neutral'
            confidence FLOAT,            -- 0.0 to 1.0

            -- Related dimensions (JSON arrays)
            sectors TEXT,                -- JSON array: ["Energy", "Technology"]
            regions TEXT,                -- JSON array: ["Middle East", "US"]

            -- Metadata
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            model_used VARCHAR(100),     -- 'gemini-3.1-flash-lite-preview'

            -- Indexes
            UNIQUE (news_id, entity_name)
        );
    """)

    # Create indexes
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_entities_name
        ON geo_macro_entities(entity_name);
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_entities_type
        ON geo_macro_entities(entity_type);
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_entities_impact
        ON geo_macro_entities(impact);
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_entities_extracted
        ON geo_macro_entities(extracted_at DESC);
    """)

    conn.commit()
    conn.close()

    logger.info("✅ geo_macro_entities table created")


def insert_entity(news_id: int, entity: Dict, model_used: str = None) -> Optional[int]:
    """Insert a single entity into geo_macro_entities.

    Args:
        news_id: News ID
        entity: Entity dict (from extractor)
        model_used: Model used for extraction

    Returns:
        Entity ID, or None if failed
    """

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Convert lists to JSON strings
        sectors_json = json.dumps(entity.get('sectors', [])) if entity.get('sectors') else None
        regions_json = json.dumps(entity.get('regions', [])) if entity.get('regions') else None

        cur.execute("""
            INSERT OR IGNORE INTO geo_macro_entities
            (news_id, entity_name, entity_type, impact, confidence, sectors, regions, model_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            news_id,
            entity.get('entity_name'),
            entity.get('entity_type'),
            entity.get('impact'),
            entity.get('confidence', 0.5),
            sectors_json,
            regions_json,
            model_used
        ))

        if cur.lastrowid:
            entity_id = cur.lastrowid
        else:
            # If INSERT OR IGNORE was triggered, find existing ID
            cur.execute("""
                SELECT id FROM geo_macro_entities
                WHERE news_id = ? AND entity_name = ?
            """, (news_id, entity.get('entity_name')))
            result = cur.fetchone()
            entity_id = result[0] if result else None

        conn.commit()
        conn.close()
        return entity_id

    except Exception as e:
        logger.warning(f"⚠️  Could not insert entity: {e}")
        conn.close()
        return None


def insert_entities_batch(news_id: int, entities: List[Dict], model_used: str = None) -> int:
    """Insert multiple entities for a news item.

    Args:
        news_id: News ID
        entities: List of entity dicts
        model_used: Model used for extraction

    Returns:
        Number of entities inserted
    """

    inserted_count = 0

    for entity in entities:
        entity_id = insert_entity(news_id, entity, model_used)
        if entity_id:
            inserted_count += 1

    return inserted_count


def get_entities_for_news(news_id: int) -> List[Dict]:
    """Get all entities for a news item.

    Args:
        news_id: News ID

    Returns:
        List of entity dicts
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM geo_macro_entities
        WHERE news_id = ?
        ORDER BY confidence DESC
    """, (news_id,))

    rows = cur.fetchall()

    # Convert to list of dicts
    columns = [desc[0] for desc in cur.description]
    entities = []
    for row in rows:
        entity_dict = dict(zip(columns, row))
        # Parse JSON fields
        if entity_dict.get('sectors'):
            try:
                entity_dict['sectors'] = json.loads(entity_dict['sectors'])
            except:
                entity_dict['sectors'] = []
        if entity_dict.get('regions'):
            try:
                entity_dict['regions'] = json.loads(entity_dict['regions'])
            except:
                entity_dict['regions'] = []
        entities.append(entity_dict)

    conn.close()
    return entities


def get_recent_entities(hours_back: int = 24, limit: int = 100) -> List[Dict]:
    """Get recent entities from database.

    Args:
        hours_back: Hours to look back
        limit: Maximum number of items

    Returns:
        List of entity dicts
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM geo_macro_entities
        WHERE extracted_at > datetime('now', '-' || ? || ' hours')
        ORDER BY extracted_at DESC
        LIMIT ?
    """, (hours_back, limit))

    rows = cur.fetchall()

    # Convert to list of dicts
    columns = [desc[0] for desc in cur.description]
    entities = []
    for row in rows:
        entity_dict = dict(zip(columns, row))
        # Parse JSON fields
        if entity_dict.get('sectors'):
            try:
                entity_dict['sectors'] = json.loads(entity_dict['sectors'])
            except:
                entity_dict['sectors'] = []
        if entity_dict.get('regions'):
            try:
                entity_dict['regions'] = json.loads(entity_dict['regions'])
            except:
                entity_dict['regions'] = []
        entities.append(entity_dict)

    conn.close()
    return entities


def get_entities_by_name(entity_name: str, hours_back: int = 24) -> List[Dict]:
    """Get all entities with a specific name.

    Args:
        entity_name: Entity name to search
        hours_back: Hours to look back

    Returns:
        List of entity dicts
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM geo_macro_entities
        WHERE entity_name = ?
        AND extracted_at > datetime('now', '-' || ? || ' hours')
        ORDER BY extracted_at DESC
    """, (entity_name, hours_back))

    rows = cur.fetchall()

    # Convert to list of dicts
    columns = [desc[0] for desc in cur.description]
    entities = []
    for row in rows:
        entity_dict = dict(zip(columns, row))
        # Parse JSON fields
        if entity_dict.get('sectors'):
            try:
                entity_dict['sectors'] = json.loads(entity_dict['sectors'])
            except:
                entity_dict['sectors'] = []
        if entity_dict.get('regions'):
            try:
                entity_dict['regions'] = json.loads(entity_dict['regions'])
            except:
                entity_dict['regions'] = []
        entities.append(entity_dict)

    conn.close()
    return entities
