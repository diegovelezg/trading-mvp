#!/usr/bin/env python3
"""
Script de Diagnóstico de Base de Datos

Verifica si el DATABASE_URL actual apunta a Supabase o a otra instancia de PostgreSQL.
"""

import os
import sys
from urllib.parse import urlparse
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL no encontrada en .env")
    sys.exit(1)

parsed = urlparse(DATABASE_URL)

print("="*70)
print("🔍 DIAGNÓSTICO DE BASE DE DATOS")
print("="*70)
print()

print("📍 Host actual:")
print(f"   Hostname: {parsed.hostname}")
print(f"   Puerto: {parsed.port}")
print(f"   Base de datos: {parsed.path[1:]}")
print()

print("🔍 Análisis del Host:")

if "supabase" in parsed.hostname.lower():
    print("   ✅ El hostname contiene 'supabase' - PROBABLEMENTE es Supabase")
elif parsed.hostname == "YOUR_DATABASE_HOST":
    print("   ⚠️  El hostname es una IP privada (YOUR_DATABASE_HOST)")
    print("   ❌ PROBABLEMENTE NO es Supabase (Supabase usa dominios públicos)")
    print()
    print("   📋 Recomendación:")
    print("      1. Verificar si YOUR_DATABASE_HOST:6544 es una instancia de PostgreSQL")
    print("      2. Si quieres usar Supabase, obtener la URL real de Supabase:")
    print("         → Dashboard de Supabase → Settings → Database → Connection string")
    print()
    print("   📖 Ver instrucciones en: docs/SUPABASE_DATABASE_CONFIG.md")
else:
    print("   ❓ Hostname desconocido - Necesita verificación manual")

print()
print("="*70)
print("📋 CONFIGURACIÓN ACTUAL")
print("="*70)
print(f"DATABASE_URL = {DATABASE_URL[:50]}...{DATABASE_URL[-20:]}")
print()

# Verificar si hay SUPABASE_DATABASE_URL
SUPABASE_DB_URL = os.getenv("SUPABASE_DATABASE_URL")
if SUPABASE_DB_URL:
    print("✅ SUPABASE_DATABASE_URL encontrada")
    print(f"   {SUPABASE_DB_URL[:50]}...")
else:
    print("❌ SUPABASE_DATABASE_URL NO encontrada")
    print()
    print("   💡 Para completar la migración a Supabase:")
    print("      1. Obtener URL de conexión de Supabase")
    print("      2. Añadir a .env: SUPABASE_DATABASE_URL=<url>")
    print("      3. Verificar con: python scripts/verify_supabase_connection.py")

print()
print("="*70)
