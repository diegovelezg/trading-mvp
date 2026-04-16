#!/usr/bin/env python3
"""Test script para verificar que todos los imports funcionan correctamente."""

import sys
import os

print("🔍 Testing Python environment...")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")
print(f"PYTHONPATH: {sys.path}")
print()

# Test 1: Import trading_mvp
print("Test 1: Import trading_mvp...")
try:
    import trading_mvp
    print("✅ trading_mvp importado correctamente")
except ImportError as e:
    print(f"❌ Error importando trading_mvp: {e}")
    sys.exit(1)

# Test 2: Import módulos principales
print("\nTest 2: Import módulos principales...")
modules_to_test = [
    'trading_mvp.core.db_watchlist',
    'trading_mvp.core.db_investment_tracking',
    'trading_mvp.agents.decision_agent',
    'trading_mvp.execution.alpaca_orders',
    'trading_mvp.core.workflow_orchestrator',
    'trading_mvp.core.news_extraction',
]

failed_imports = []
for module in modules_to_test:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError as e:
        print(f"❌ {module}: {e}")
        failed_imports.append(module)

if failed_imports:
    print(f"\n❌ {len(failed_imports)} módulos fallaron")
    sys.exit(1)

# Test 3: Verificar dependencias externas
print("\nTest 3: Verificar dependencias externas...")
deps_to_test = [
    'alpaca',
    'google.generativeai',
    'dotenv',
    'pytz',
    'psycopg2',
    'supabase',
    'requests',
    'pandas',
    'numpy',
]

failed_deps = []
for dep in deps_to_test:
    try:
        __import__(dep)
        print(f"✅ {dep}")
    except ImportError as e:
        print(f"❌ {dep}: {e}")
        failed_deps.append(dep)

if failed_deps:
    print(f"\n❌ {len(failed_deps)} dependencias fallaron")
    sys.exit(1)

print("\n" + "="*50)
print("✅ ALL TESTS PASSED!")
print("="*50)
print("\nEl entorno está correctamente configurado.")
print("Puedes ejecutar: python ejecutar_mesa_inversiones")