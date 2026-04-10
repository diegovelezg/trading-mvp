#!/usr/bin/env python3
"""
Verificar Conexión a Supabase

Script para verificar que la conexión a Supabase funciona correctamente.
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

def verify_supabase_connection():
    """Verifica si la conexión a Supabase funciona."""

    # Intentar usar SUPABASE_DATABASE_URL primero
    db_url = os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL")

    if not db_url:
        print("❌ No se encontró DATABASE_URL ni SUPABASE_DATABASE_URL")
        return False

    print(f"🔍 Verificando conexión a base de datos...")
    print(f"   Host: {db_url.split('@')[1].split('/')[0] if '@' in db_url else 'unknown'}")
    print()

    try:
        from trading_mvp.core.db_manager import get_connection

        conn = get_connection()
        print("✅ Conexión exitosa a PostgreSQL")

        # Verificar que las tablas existen
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)

            tables = [row[0] for row in cur.fetchall()]

            print(f"📊 Tablas encontradas: {len(tables)}")

            # Tablas críticas que deben existir
            critical_tables = ['watchlists', 'watchlist_items', 'explorations', 'news']
            missing_tables = [t for t in critical_tables if t not in tables]

            if missing_tables:
                print(f"⚠️  Tablas faltantes: {missing_tables}")
            else:
                print("✅ Todas las tablas críticas existen")

        conn.close()
        print()
        print("="*70)
        print("✅ VERIFICACIÓN COMPLETADA - Base de datos accesible")
        print("="*70)
        return True

    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print()
        print("💡 Posibles soluciones:")
        print("   1. Verificar que SUPABASE_DATABASE_URL es correcta")
        print("   2. Verificar que el servidor es accesible")
        print("   3. Verificar credenciales")
        return False

if __name__ == "__main__":
    verify_supabase_connection()
