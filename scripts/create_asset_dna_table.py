#!/usr/bin/env python3
"""Crear tabla asset_dna en Supabase."""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

import psycopg2
from psycopg2 import errors as psycopg2_errors

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no encontrada")
    sys.exit(1)

def create_asset_dna_table():
    """Crear tabla asset_dna en Supabase."""

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            # Primero verificar si la extensión vector está habilitada
            print("Verificando extensión vector...")
            cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector';")
            if not cur.fetchone():
                print("⚠️  La extensión 'vector' no está habilitada.")
                print("   Ejecutando: CREATE EXTENSION IF NOT EXISTS vector;")
                try:
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    print("✅ Extensión vector habilitada")
                except Exception as e:
                    print(f"⚠️  No se pudo habilitar la extensión vector: {e}")
                    print("   Continuando sin soporte de embeddings...")

            # Crear tabla asset_dna
            print("Creando tabla asset_dna...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS asset_dna (
                    ticker VARCHAR(10) PRIMARY KEY,
                    asset_type VARCHAR(255) NOT NULL,
                    core_drivers TEXT[] NOT NULL,
                    bullish_catalysts TEXT[] NOT NULL,
                    bearish_catalysts TEXT[] NOT NULL,
                    geopolitical_sensitivity FLOAT DEFAULT 0.5,
                    interest_rate_sensitivity FLOAT DEFAULT 0.5,
                    embedding VECTOR(1536),
                    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ Tabla asset_dna creada")

            # Crear índices
            print("Creando índices...")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_asset_dna_ticker ON asset_dna(ticker);")

            # Intentar crear índice de embeddings solo si la extensión está habilitada
            try:
                cur.execute("CREATE INDEX IF NOT EXISTS idx_asset_dna_embedding ON asset_dna USING ivfflat (embedding vector_cosine_ops);")
                print("✅ Índice de embeddings creado")
            except Exception as e:
                print(f"⚠️  No se pudo crear índice de embeddings: {e}")

            print("✅ Índices creados")

            # Habilitar RLS
            print("Configurando RLS (Row Level Security)...")
            cur.execute("ALTER TABLE asset_dna ENABLE ROW LEVEL SECURITY;")

            # Crear políticas (manejo manual de IF NOT EXISTS)
            print("Creando políticas de acceso...")

            # Política 1: Lectura pública
            try:
                cur.execute("""
                    CREATE POLICY "Allow public read access" ON asset_dna
                    FOR SELECT
                    USING (true);
                """)
                print("✅ Política de lectura pública creada")
            except psycopg2_errors.DuplicateObject:
                print("ℹ️  Política de lectura pública ya existe")

            # Política 2: Inserción service_role
            try:
                cur.execute("""
                    CREATE POLICY "Allow service role insert" ON asset_dna
                    FOR INSERT
                    WITH CHECK (true);
                """)
                print("✅ Política de inserción service_role creada")
            except psycopg2_errors.DuplicateObject:
                print("ℹ️  Política de inserción service_role ya existe")

            # Política 3: Actualización service_role
            try:
                cur.execute("""
                    CREATE POLICY "Allow service role update" ON asset_dna
                    FOR UPDATE
                    USING (true)
                    WITH CHECK (true);
                """)
                print("✅ Política de actualización service_role creada")
            except psycopg2_errors.DuplicateObject:
                print("ℹ️  Política de actualización service_role ya existe")

            print()
            print("="*70)
            print("✅ TABLA asset_dna CREADA EXITOSAMENTE")
            print("="*70)
            print()
            print("📋 Estructura:")
            print("   - ticker: VARCHAR(10) PRIMARY KEY")
            print("   - asset_type: Tipo de activo")
            print("   - core_drivers: TEXT[] - Factores principales")
            print("   - bullish_catalysts: TEXT[] - Catalistas alcistas")
            print("   - bearish_catalysts: TEXT[] - Catalistas bajistas")
            print("   - geopolitical_sensitivity: FLOAT (0.0-1.0)")
            print("   - interest_rate_sensitivity: FLOAT (0.0-1.0)")
            print("   - embedding: VECTOR(1536) - Para búsquedas semánticas")
            print()

    except Exception as e:
        print(f"❌ Error creando tabla asset_dna: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    create_asset_dna_table()
