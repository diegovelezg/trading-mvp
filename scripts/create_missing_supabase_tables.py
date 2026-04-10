#!/usr/bin/env python3
"""Crear tablas faltantes en Supabase."""

import os
import sys
from supabase import create_client

# Cargar variables de entorno
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv

load_dotenv()

# Configurar Supabase client
supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: Variables de entorno de Supabase no encontradas")
    sys.exit(1)

# Nota: Para crear tablas en Supabase, necesitamos usar la API SQL o el dashboard
# El cliente Python de Supabase no tiene método directo para crear tablas
# En su lugar, usaremos la URL de DATABASE_URL con psycopg2 para ejecutar SQL

import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no encontrada")
    sys.exit(1)

def create_missing_tables():
    """Crear tablas faltantes en Supabase."""

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            # Tabla: geo_entities
            print("Creando tabla geo_entities...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS geo_entities (
                    id SERIAL PRIMARY KEY,
                    entity_name VARCHAR(255) NOT NULL UNIQUE,
                    entity_type VARCHAR(50),
                    countries TEXT[],
                    sectors TEXT[],
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ geo_entities creada")

            # Tabla: investment_runs (mesa de inversiones)
            print("Creando tabla investment_runs...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS investment_runs (
                    id SERIAL PRIMARY KEY,
                    watchlist_id INTEGER,
                    watchlist_name VARCHAR(255),
                    analysis_timestamp TIMESTAMP WITH TIME ZONE,
                    time_window_hours INTEGER,
                    duration_seconds FLOAT,

                    -- Aggregate metrics
                    total_tickers INTEGER,
                    analyzed_tickers INTEGER,
                    avg_confidence FLOAT,
                    avg_negative_ratio FLOAT,
                    avg_positive_ratio FLOAT,
                    total_news_analyzed INTEGER,
                    total_entities_found INTEGER,

                    -- Recommendation breakdown
                    bullish_count INTEGER,
                    bearish_count INTEGER,
                    cautious_count INTEGER,
                    neutral_count INTEGER,

                    -- Overall sentiment
                    overall_sentiment VARCHAR(50),
                    desk_outlook TEXT,

                    -- Created at
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ investment_runs creada")

            # Tabla: ticker_analysis
            print("Creando tabla ticker_analysis...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ticker_analysis (
                    id SERIAL PRIMARY KEY,
                    desk_run_id INTEGER REFERENCES investment_runs(id) ON DELETE CASCADE,

                    -- Ticker info
                    ticker VARCHAR(10) NOT NULL,
                    company_name VARCHAR(255),

                    -- Recommendation
                    recommendation VARCHAR(20), -- BULLISH, BEARISH, CAUTIOUS, NEUTRAL
                    rationale TEXT,

                    -- Sentiment scores
                    positive_ratio FLOAT,
                    negative_ratio FLOAT,
                    neutral_ratio FLOAT,
                    avg_confidence FLOAT,

                    -- News analysis
                    related_news_count INTEGER,
                    unique_entities_found INTEGER,

                    -- Top risks and opportunities (JSON)
                    top_risks JSONB,
                    top_opportunities JSONB,

                    -- Metadata
                    is_in_portfolio BOOLEAN DEFAULT FALSE,
                    analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ ticker_analysis creada")

            # Crear índices
            print("Creando índices...")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_ticker_analysis_desk_run ON ticker_analysis(desk_run_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_ticker_analysis_ticker ON ticker_analysis(ticker);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_investment_runs_timestamp ON investment_runs(analysis_timestamp DESC);")
            print("✅ Índices creados")

            print()
            print("="*70)
            print("✅ TODAS LAS TABLAS CREADAS EXITOSAMENTE")
            print("="*70)

    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    create_missing_tables()
