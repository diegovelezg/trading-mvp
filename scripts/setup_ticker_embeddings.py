#!/usr/bin/env python3
"""
Setup ticker entity embeddings table in PostgreSQL with vector support.

Requiere: pgvector extension instalado en Supabase
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from trading_mvp.core.db_manager import get_connection

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def setup_ticker_embeddings_table():
    """Create ticker entity embeddings table with vector support."""

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Habilitar pgvector extension (si no está habilitada)
            logger.info("📦 Enabling pgvector extension...")
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            logger.info("   ✅ pgvector extension enabled")

            # 2. Crear tabla de embeddings
            logger.info("📋 Creating ticker_entity_embeddings table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ticker_entity_embeddings (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(10) NOT NULL,
                    entity_text VARCHAR(255) NOT NULL,
                    embedding VECTOR(768) NOT NULL,
                    task_type VARCHAR(50) DEFAULT 'SEMANTIC_SIMILARITY',
                    model_name VARCHAR(100) DEFAULT 'gemini-embedding-001',
                    output_dimensionality INTEGER DEFAULT 768,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (ticker, entity_text)
                );
            """)
            logger.info("   ✅ Table created")

            # 3. Crear índices para búsqueda vectorial rápida
            logger.info("🔍 Creating vector indexes...")
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_ticker_embeddings_ticker
                ON ticker_entity_embeddings(ticker);
            """)

            # Índice HNSW para búsqueda vectorial rápida (cosine similarity)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_ticker_embeddings_vector
                ON ticker_entity_embeddings
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """)
            logger.info("   ✅ HNSW index created for vector search")

            # 4. Crear índice para texto
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_ticker_embeddings_entity_text
                ON ticker_entity_embeddings(entity_text);
            """)
            logger.info("   ✅ Text index created")

            # 5. Crear trigger para updated_at
            cur.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """)

            cur.execute("""
                DROP TRIGGER IF EXISTS update_ticker_embeddings_updated_at
                ON ticker_entity_embeddings;
            """)

            cur.execute("""
                CREATE TRIGGER update_ticker_embeddings_updated_at
                BEFORE UPDATE ON ticker_entity_embeddings
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            """)
            logger.info("   ✅ updated_at trigger created")

            conn.commit()
            logger.info("")
            logger.info("="*70)
            logger.info("✅ TICKER ENTITY EMBEDDINGS TABLE SETUP COMPLETE")
            logger.info("="*70)
            logger.info("   Table: ticker_entity_embeddings")
            logger.info("   Vector size: 768")
            logger.info("   Index: HNSW (cosine similarity)")
            logger.info("   Model: gemini-embedding-001")
            logger.info("="*70)

    except Exception as e:
        logger.error(f"❌ Error setting up embeddings table: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    setup_ticker_embeddings_table()
