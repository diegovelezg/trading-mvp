#!/usr/bin/env python3
"""Script para verificar el estado de las tablas en Supabase."""

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
    print("   Necesito: NEXT_PUBLIC_SUPABASE_URL y NEXT_PUBLIC_SUPABASE_ANON_KEY")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_key)

def check_table(table_name: str):
    """Verifica si una tabla existe y retorna información básica."""
    try:
        # Intentar hacer un query simple
        result = supabase.table(table_name).select("*").limit(1).execute()

        count = len(result.data)
        print(f"✅ {table_name:25s} - EXISTS ({count} rows sample)")
        return True
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
            print(f"❌ {table_name:25s} - NOT FOUND")
        else:
            print(f"⚠️  {table_name:25s} - ERROR: {error_msg[:50]}")
        return False

def main():
    print("="*70)
    print("🔍 DIAGNÓSTICO DE TABLAS SUPABASE")
    print("="*70)
    print()

    # Tablas que deberían existir
    tables_to_check = [
        "watchlists",
        "watchlist_items",
        "watchlist_analysis",
        "explorations",
        "news",
        "sentiments",
        "geo_entities",
        "investment_desk_runs",
        "ticker_analyses",
        "investment_decisions"
    ]

    print("Tablas requeridas por el sistema:")
    print("-"*70)

    existing_tables = []
    missing_tables = []

    for table in tables_to_check:
        if check_table(table):
            existing_tables.append(table)
        else:
            missing_tables.append(table)

    print()
    print("="*70)
    print("RESUMEN")
    print("="*70)
    print(f"✅ Tablas existentes: {len(existing_tables)}")
    print(f"❌ Tablas faltantes:  {len(missing_tables)}")

    if missing_tables:
        print()
        print("Tablas que necesitan ser creadas:")
        for table in missing_tables:
            print(f"  - {table}")

if __name__ == "__main__":
    main()
