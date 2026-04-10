#!/usr/bin/env python3
"""Arreglar esquema de tablas en Supabase para que coincida con PostgreSQL local."""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no encontrada")
    sys.exit(1)

def fix_supabase_schema():
    """Arreglar esquema de Supabase."""

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            print("="*70)
            print("🔧 ARREGLANDO ESQUEMA SUPABASE")
            print("="*70)
            print()

            # 1. Verificar si existe la tabla geo_entities (incorrecta)
            print("1️⃣  Verificando tabla geo_entities...")
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'geo_entities'
                );
            """)
            geo_entities_exists = cur.fetchone()[0]

            if geo_entities_exists:
                print("   ⚠️  Tabla 'geo_entities' encontrada (esquema incorrecto)")
                print("   💡 Opción: Renombrar a 'geo_entities_old' y crear tabla correcta")

                # Renombrar tabla incorrecta
                cur.execute("ALTER TABLE geo_entities RENAME TO geo_entities_old;")
                print("   ✅ Renombrada a 'geo_entities_old'")
            else:
                print("   ✅ Tabla 'geo_entities' no existe (bien)")

            print()

            # 2. Crear tabla correcta: geo_macro_entities
            print("2️⃣  Creando tabla correcta: geo_macro_entities...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS geo_macro_entities (
                    id SERIAL PRIMARY KEY,

                    -- Relation to news
                    news_id INTEGER NOT NULL,

                    -- Entity information
                    entity_name VARCHAR(255) NOT NULL,
                    entity_type VARCHAR(50),
                    impact VARCHAR(20),
                    confidence FLOAT,

                    -- Related dimensions (JSONB for Postgres)
                    sectors JSONB,
                    regions JSONB,

                    -- Metadata
                    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_used VARCHAR(100),

                    -- Indexes
                    UNIQUE (news_id, entity_name)
                );
            """)
            print("   ✅ Tabla 'geo_macro_entities' creada")

            # Crear índices
            print("   📊 Creando índices...")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_entities_name ON geo_macro_entities(entity_name);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON geo_macro_entities(entity_type);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_entities_impact ON geo_macro_entities(impact);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_entities_extracted ON geo_macro_entities(extracted_at DESC);")
            print("   ✅ Índices creados")

            print()

            # 3. Verificar tabla geo_macro_news
            print("3️⃣  Verificando tabla geo_macro_news...")
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'geo_macro_news'
                );
            """)
            geo_news_exists = cur.fetchone()[0]

            if geo_news_exists:
                print("   ✅ Tabla 'geo_macro_news' existe")

                # Verificar si tiene la columna alpaca_id
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns
                        WHERE table_name = 'geo_macro_news'
                        AND column_name = 'alpaca_id'
                    );
                """)
                has_alpaca_id = cur.fetchone()[0]

                if has_alpaca_id:
                    print("   ✅ Columna 'alpaca_id' existe")
                else:
                    print("   ⚠️  Columna 'alpaca_id' NO existe - agregando...")
                    cur.execute("ALTER TABLE geo_macro_news ADD COLUMN IF NOT EXISTS alpaca_id INTEGER;")
                    print("   ✅ Columna 'alpaca_id' agregada")
            else:
                print("   ⚠️  Tabla 'geo_macro_news' NO existe - creando...")
                cur.execute("""
                    CREATE TABLE geo_macro_news (
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
                print("   ✅ Tabla 'geo_macro_news' creada")

            print()

            # 4. Verificar tablas de mesa de inversiones
            print("4️⃣  Verificando tablas de mesa de inversiones...")

            # investment_runs
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'investment_runs'
                );
            """)
            if not cur.fetchone()[0]:
                print("   💾 Creando tabla 'investment_runs'...")
                cur.execute("""
                    CREATE TABLE investment_runs (
                        id SERIAL PRIMARY KEY,
                        watchlist_id INTEGER,
                        watchlist_name VARCHAR(255),
                        theme VARCHAR(255),
                        overall_sentiment VARCHAR(50),
                        total_tickers INTEGER,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                print("   ✅ Creada")
            else:
                print("   ✅ Tabla 'investment_runs' existe")

            # ticker_analysis
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'ticker_analysis'
                );
            """)
            if not cur.fetchone()[0]:
                print("   💾 Creando tabla 'ticker_analysis'...")
                cur.execute("""
                    CREATE TABLE ticker_analysis (
                        id SERIAL PRIMARY KEY,
                        desk_run_id INTEGER REFERENCES investment_runs(id) ON DELETE CASCADE,
                        ticker VARCHAR(10) NOT NULL,
                        company_name VARCHAR(255),
                        recommendation VARCHAR(20),
                        rationale TEXT,
                        positive_ratio FLOAT,
                        negative_ratio FLOAT,
                        avg_confidence FLOAT,
                        related_news_count INTEGER,
                        unique_entities_found INTEGER,
                        is_in_portfolio BOOLEAN DEFAULT FALSE,
                        analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                print("   ✅ Creada")
            else:
                print("   ✅ Tabla 'ticker_analysis' existe")

            print()
            print("="*70)
            print("✅ ESQUEMA SUPABASE ARREGLADO EXITOSAMENTE")
            print("="*70)
            print()
            print("📋 Tablas verificadas/creadas:")
            print("   ✅ geo_macro_entities (con news_id)")
            print("   ✅ geo_macro_news (con alpaca_id)")
            print("   ✅ investment_runs")
            print("   ✅ ticker_analysis")
            print()
            print("🚀 Ahora puedes ejecutar la mesa de inversiones correctamente")

    except Exception as e:
        print(f"❌ Error arreglando esquema: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    fix_supabase_schema()
