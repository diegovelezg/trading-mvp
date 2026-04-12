"""
Database operations for ticker entity embeddings.
"""

import logging
from typing import List, Dict, Optional
from trading_mvp.core.db_manager import get_connection
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


def save_ticker_entity_embedding(
    ticker: str,
    entity_text: str,
    embedding: List[float],
    task_type: str = "SEMANTIC_SIMILARITY",
    model_name: str = "gemini-embedding-001"
) -> bool:
    """
    Save embedding for a ticker entity.

    Args:
        ticker: Ticker symbol
        entity_text: Entity text (e.g., "Nuclear Power")
        embedding: Embedding vector (768 dimensions)
        task_type: Gemini task type
        model_name: Model used

    Returns:
        True if saved successfully
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Convertir embedding a string vector de PostgreSQL
            embedding_str = f"[{','.join(map(str, embedding))}]"

            cur.execute("""
                INSERT INTO ticker_entity_embeddings
                (ticker, entity_text, embedding, task_type, model_name, output_dimensionality)
                VALUES (%s, %s, %s::vector(768), %s, %s, %s)
                ON CONFLICT (ticker, entity_text)
                DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    updated_at = CURRENT_TIMESTAMP
            """, (ticker.upper(), entity_text, embedding_str, task_type, model_name, len(embedding)))

            conn.commit()
            logger.debug(f"✅ Saved embedding: {ticker} → {entity_text}")
            return True

    except Exception as e:
        logger.error(f"❌ Error saving embedding for {ticker} → {entity_text}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def save_ticker_entity_embeddings_batch(
    ticker: str,
    entity_embeddings: Dict[str, List[float]],
    task_type: str = "SEMANTIC_SIMILARITY",
    model_name: str = "gemini-embedding-001"
) -> int:
    """
    Save multiple embeddings for a ticker.

    Args:
        ticker: Ticker symbol
        entity_embeddings: Dict {entity_text: embedding}
        task_type: Gemini task type
        model_name: Model used

    Returns:
        Number of embeddings saved
    """
    saved_count = 0

    for entity_text, embedding in entity_embeddings.items():
        if save_ticker_entity_embedding(ticker, entity_text, embedding, task_type, model_name):
            saved_count += 1

    return saved_count


def get_ticker_embeddings(ticker: str) -> List[Dict]:
    """
    Get all embeddings for a ticker.

    Args:
        ticker: Ticker symbol

    Returns:
        List of dicts with keys:
        - entity_text: str
        - embedding: List[float]
        - model_name: str
        - output_dimensionality: int
        - created_at: datetime
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    entity_text,
                    embedding::text::vector as embedding,
                    model_name,
                    output_dimensionality,
                    created_at
                FROM ticker_entity_embeddings
                WHERE ticker = %s
                ORDER BY entity_text
            """, (ticker.upper(),))

            results = []
            for row in cur.fetchall():
                # Convertir vector de PostgreSQL a lista de Python
                embedding_str = row['embedding']
                # Vector viene como '[0.1,0.2,...]', parseamos
                embedding_list = [float(x) for x in embedding_str.strip('[]').split(',')]

                results.append({
                    'entity_text': row['entity_text'],
                    'embedding': embedding_list,
                    'model_name': row['model_name'],
                    'output_dimensionality': row['output_dimensionality'],
                    'created_at': row['created_at']
                })

            return results

    except Exception as e:
        logger.error(f"❌ Error getting embeddings for {ticker}: {e}")
        return []
    finally:
        conn.close()


def delete_ticker_embeddings(ticker: str) -> int:
    """
    Delete all embeddings for a ticker.

    Args:
        ticker: Ticker symbol

    Returns:
        Number of embeddings deleted
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM ticker_entity_embeddings
                WHERE ticker = %s
            """, (ticker.upper(),))

            conn.commit()
            deleted_count = cur.rowcount

            if deleted_count > 0:
                logger.info(f"✅ Deleted {deleted_count} embeddings for {ticker}")

            return deleted_count

    except Exception as e:
        logger.error(f"❌ Error deleting embeddings for {ticker}: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()


def get_all_tickers_with_embeddings() -> List[str]:
    """
    Get list of tickers that have embeddings.

    Returns:
        List of ticker symbols
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT ticker
                FROM ticker_entity_embeddings
                ORDER BY ticker
            """)

            tickers = [row[0] for row in cur.fetchall()]
            return tickers

    except Exception as e:
        logger.error(f"❌ Error getting tickers with embeddings: {e}")
        return []
    finally:
        conn.close()


def get_embeddings_stats() -> Dict:
    """
    Get statistics about embeddings in database.

    Returns:
        Dict with stats
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Total embeddings
            cur.execute("SELECT COUNT(*) FROM ticker_entity_embeddings")
            total_embeddings = cur.fetchone()[0]

            # Unique tickers
            cur.execute("SELECT COUNT(DISTINCT ticker) FROM ticker_entity_embeddings")
            unique_tickers = cur.fetchone()[0]

            # Unique entities
            cur.execute("SELECT COUNT(DISTINCT entity_text) FROM ticker_entity_embeddings")
            unique_entities = cur.fetchone()[0]

            return {
                'total_embeddings': total_embeddings,
                'unique_tickers': unique_tickers,
                'unique_entities': unique_entities
            }

    except Exception as e:
        logger.error(f"❌ Error getting embeddings stats: {e}")
        return {}
    finally:
        conn.close()
