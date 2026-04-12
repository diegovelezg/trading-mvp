"""
News Embeddings Database Operations

Almacena y consulta embeddings de noticias para búsqueda semántica.
"""

import logging
from typing import List, Dict, Optional
from trading_mvp.core.db_manager import get_connection

logger = logging.getLogger(__name__)


def create_news_embeddings_table():
    """Create news_embeddings table with pgvector support."""

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Enable pgvector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            # Create table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS news_embeddings (
                    news_id INTEGER PRIMARY KEY,
                    embedding vector(768),
                    embedding_dim INTEGER DEFAULT 768,
                    embedding_model TEXT DEFAULT 'gemini-embedding-001',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (news_id) REFERENCES geo_macro_news(id) ON DELETE CASCADE
                );
            """)

            # HNSW index for fast cosine similarity search
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_news_embeddings_hnsw
                ON news_embeddings USING hnsw (embedding vector_cosine_ops);
            """)

            # Index for news_id lookups
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_news_embeddings_news_id
                ON news_embeddings(news_id);
            """)

        conn.commit()
        logger.info("✅ news_embeddings table created")

    except Exception as e:
        logger.error(f"❌ Failed to create news_embeddings table: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def save_news_embedding(news_id: int, embedding: List[float], model: str = "gemini-embedding-001") -> bool:
    """Save or update embedding for a news item.

    Args:
        news_id: News ID
        embedding: Embedding vector (768 dims)
        model: Embedding model used

    Returns:
        True if successful
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Use INSERT ... ON CONFLICT for upsert
            cur.execute("""
                INSERT INTO news_embeddings (news_id, embedding, embedding_dim, embedding_model, updated_at)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (news_id) DO UPDATE
                SET embedding = EXCLUDED.embedding,
                    updated_at = CURRENT_TIMESTAMP
            """, (news_id, str(embedding), len(embedding), model))

        conn.commit()
        return True

    except Exception as e:
        logger.error(f"❌ Failed to save news embedding {news_id}: {e}")
        return False
    finally:
        conn.close()


def get_news_embedding(news_id: int) -> Optional[List[float]]:
    """Get embedding for a news item.

    Args:
        news_id: News ID

    Returns:
        Embedding vector or None
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT embedding
                FROM news_embeddings
                WHERE news_id = %s
            """, (news_id,))

            result = cur.fetchone()
            if result:
                # Parse vector string back to list
                vector_str = result[0]
                # Remove brackets and split
                embedding = [float(x) for x in vector_str.strip('[]').split(',')]
                return embedding

        return None

    except Exception as e:
        logger.error(f"❌ Failed to get news embedding {news_id}: {e}")
        return None
    finally:
        conn.close()


def find_similar_news(
    query_embedding: List[float],
    threshold: float = 0.75,
    limit: int = 50
) -> List[Dict]:
    """Find news similar to a query embedding using cosine similarity.

    Args:
        query_embedding: Query embedding vector
        threshold: Minimum cosine similarity (0-1)
        limit: Max results

    Returns:
        List of (news_id, similarity) tuples
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    news_id,
                    1 - (embedding <=> %s::vector) as similarity
                FROM news_embeddings
                WHERE 1 - (embedding <=> %s::vector) >= %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (str(query_embedding), str(query_embedding), threshold, str(query_embedding), limit))

            results = cur.fetchall()

            return [
                {
                    'news_id': row[0],
                    'similarity': row[1]
                }
                for row in results
            ]

    except Exception as e:
        logger.error(f"❌ Failed to find similar news: {e}")
        return []
    finally:
        conn.close()


def get_news_embeddings_batch(news_ids: List[int]) -> Dict[int, List[float]]:
    """Get embeddings for multiple news items efficiently.

    Args:
        news_ids: List of news IDs

    Returns:
        Dict mapping news_id -> embedding
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT news_id, embedding
                FROM news_embeddings
                WHERE news_id = ANY(%s)
            """, (news_ids,))

            results = cur.fetchall()

            # Parse vectors
            embeddings_map = {}
            for news_id, vector_str in results:
                embedding = [float(x) for x in vector_str.strip('[]').split(',')]
                embeddings_map[news_id] = embedding

            return embeddings_map

    except Exception as e:
        logger.error(f"❌ Failed to get batch embeddings: {e}")
        return {}
    finally:
        conn.close()


def count_news_embeddings() -> int:
    """Count total news embeddings in database.

    Returns:
        Count of embeddings
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM news_embeddings")
            count = cur.fetchone()[0]
            return count

    except Exception as e:
        logger.error(f"❌ Failed to count embeddings: {e}")
        return 0
    finally:
        conn.close()


def get_unembedded_news(limit: int = 100) -> List[int]:
    """Get news items that don't have embeddings yet.

    Args:
        limit: Max results

    Returns:
        List of news IDs
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT n.id
                FROM geo_macro_news n
                LEFT JOIN news_embeddings e ON n.id = e.news_id
                WHERE e.news_id IS NULL
                ORDER BY n.published_at DESC
                LIMIT %s
            """, (limit,))

            results = cur.fetchall()
            return [row[0] for row in results]

    except Exception as e:
        logger.error(f"❌ Failed to get unembedded news: {e}")
        return []
    finally:
        conn.close()
