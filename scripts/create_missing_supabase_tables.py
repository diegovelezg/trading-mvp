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

            # 1. Desk runs (complete investment desk analysis)
            print("Creando tabla investment_desk_runs...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS investment_desk_runs (
                    id SERIAL PRIMARY KEY,
                    run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    watchlist_id INTEGER NOT NULL,
                    watchlist_name VARCHAR(255),
                    time_window_hours INTEGER,
                    duration_seconds FLOAT,
                    overall_sentiment VARCHAR(50),
                    desk_outlook TEXT,
                    total_tickers INTEGER,
                    analyzed_tickers INTEGER,
                    failed_tickers TEXT,
                    total_news_analyzed INTEGER,
                    total_entities_found INTEGER,
                    avg_confidence FLOAT,
                    avg_negative_ratio FLOAT,
                    avg_positive_ratio FLOAT,
                    bullish_count INTEGER,
                    bearish_count INTEGER,
                    cautious_count INTEGER,
                    neutral_count INTEGER,
                    full_results_json TEXT,
                    recommendations_json TEXT
                );
            """)
            print("✅ investment_desk_runs creada")

            # 2. Individual ticker analyses
            print("Creando tabla ticker_analyses...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ticker_analyses (
                    id SERIAL PRIMARY KEY,
                    desk_run_id INTEGER REFERENCES investment_desk_runs(id) ON DELETE CASCADE,
                    ticker VARCHAR(10) NOT NULL,
                    company_name VARCHAR(255),
                    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    mapped_entities TEXT,
                    related_news_count INTEGER,
                    news_sources TEXT,
                    news_ids TEXT,
                    unique_entities_found INTEGER,
                    total_entity_mentions INTEGER,
                    avg_confidence FLOAT,
                    negative_ratio FLOAT,
                    positive_ratio FLOAT,
                    recommendation VARCHAR(50),
                    rationale TEXT,
                    top_risks_json TEXT,
                    top_opportunities_json TEXT,
                    most_mentioned_json TEXT,
                    full_results_json TEXT
                );
            """)
            print("✅ ticker_analyses creada")

            # 3. Decision tracking
            print("Creando tabla investment_decisions...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS investment_decisions (
                    id SERIAL PRIMARY KEY,
                    ticker_analysis_id INTEGER NOT NULL REFERENCES ticker_analyses(id) ON DELETE CASCADE,
                    desk_run_id INTEGER NOT NULL REFERENCES investment_desk_runs(id) ON DELETE CASCADE,
                    ticker VARCHAR(10) NOT NULL,
                    alpaca_order_id TEXT,
                    recommendation VARCHAR(50),
                    desk_action VARCHAR(50),
                    decision VARCHAR(50),
                    decision_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    decision_notes TEXT,
                    action_taken VARCHAR(100),
                    execution_timestamp TIMESTAMP,
                    position_size FLOAT,
                    entry_price FLOAT,
                    target_price FLOAT,
                    stop_loss FLOAT,
                    exit_price FLOAT,
                    exit_timestamp TIMESTAMP,
                    profit_loss FLOAT,
                    profit_loss_pct FLOAT,
                    status VARCHAR(50) DEFAULT 'PENDING'
                );
            """)
            print("✅ investment_decisions creada")

            # Crear índices
            print("Creando índices...")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_ticker_analyses_desk_run ON ticker_analyses(desk_run_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_ticker_analyses_ticker ON ticker_analyses(ticker);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_investment_desk_runs_timestamp ON investment_desk_runs(run_timestamp DESC);")
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
