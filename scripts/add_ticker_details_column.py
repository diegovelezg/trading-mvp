#!/usr/bin/env python3
"""Añade la columna ticker_details a la tabla explorations en Supabase."""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()

def add_column_via_psycopg2():
    """Ejecuta ALTER TABLE usando psycopg2 y DATABASE_URL."""

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ DATABASE_URL not found in .env")
        return False

    print(f"🔗 Conectando a PostgreSQL...")

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        print("✅ Conexión exitosa!")

        # SQL commands
        sql_commands = [
            """
            ALTER TABLE explorations
            ADD COLUMN IF NOT EXISTS ticker_details JSONB DEFAULT '[]'::jsonb;
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_explorations_ticker_details
            ON explorations USING GIN (ticker_details);
            """,
            """
            COMMENT ON COLUMN explorations.ticker_details
            IS 'JSON completo con metadatos de tickers descubiertos: [{ticker, name, sector, description_es}]';
            """
        ]

        for i, command in enumerate(sql_commands, 1):
            print(f"📊 Ejecutando comando {i}/{len(sql_commands)}...")
            cursor.execute(command)
            print(f"   ✅ Comando {i} ejecutado")

        # Commit los cambios
        conn.commit()
        print("\n✅ Todos los cambios aplicados exitosamente!")

        # Verificar que la columna existe
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'explorations'
            AND column_name = 'ticker_details';
        """)

        result = cursor.fetchone()
        if result:
            print(f"✅ Verificación: Columna '{result[0]}' de tipo '{result[1]}' existe!")
        else:
            print("⚠️  Warning: Columna no encontrada después de crearla")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Añadiendo columna ticker_details a explorations\n")
    add_column_via_psycopg2()
