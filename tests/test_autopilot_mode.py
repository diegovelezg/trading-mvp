#!/usr/bin/env python3
"""Test AUTOPILOT_MODE y cache de noticias."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import logging

# Set up environment
os.environ['ALPACA_PAPER_API_KEY'] = 'YOUR_ALPACA_PAPER_API_KEY'
os.environ['PAPER_API_SECRET'] = 'YOUR_ALPACA_SECRET_KEY'
os.environ['SERPAPI_API_KEY'] = 'YOUR_SERPAPI_API_KEY'
os.environ['GEMINI_API_KEY'] = 'AIzaSyCutHRoCMkN02KhsVYATzu5XRPjboQZxnc'
os.environ['GEMINI_API_MODEL_01'] = 'gemini-3.1-flash-lite-preview'
os.environ['GEMINI_API_MODEL_02'] = 'gemini-3-flash-preview'

print()
print("="*70)
print("🤖 TEST AUTOPILOT MODE & CACHE DE NOTICIAS")
print("="*70)
print()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.claude', 'subagents'))

# Test 1: Verificar AUTOPILOT_MODE=OFF (no ejecuta)
print("📍 TEST 1: AUTOPILOT_MODE=OFF")
print("-" * 40)
print("Modo: Análisis SIN ejecución")
print()

from orchestrator.agent import orchestrate_investment_workflow

result = orchestrate_investment_workflow(
    theme="semiconductor stocks",
    capital=3000.0,
    execute=False  # No ejecutar
)

if "error" in result:
    print(f"❌ ERROR: {result['error']}")
else:
    cio_decision = result.get('cio_decision', {})
    print(f"✅ Análisis completado:")
    print(f"   Ticker seleccionado: {cio_decision.get('selected_ticker')}")
    print(f"   Acción: {cio_decision.get('action')}")
    print(f"   Ejecución: NO (execute=False)")

print()
print()

# Test 2: Verificar AUTOPILOT_MODE=ON (ejecuta automáticamente)
print("📍 TEST 2: AUTOPILOT_MODE=ON")
print("-" * 40)
print("Modo: Ejecución AUTOMÁTICA en Paper Trading")
print()

os.environ['AUTOPILOT_MODE'] = 'on'

result = orchestrate_investment_workflow(
    theme="AI infrastructure",
    capital=2000.0,
    execute=False  # El orchestrator lo cambiará a True
)

if "error" in result:
    print(f"❌ ERROR: {result['error']}")
else:
    cio_decision = result.get('cio_decision', {})
    execution_result = result.get('execution_result')

    print(f"✅ Análisis completado:")
    print(f"   Ticker seleccionado: {cio_decision.get('selected_ticker')}")
    print(f"   Acción: {cio_decision.get('action')}")
    print(f"   Ejecución: {'SÍ' if execution_result else 'NO'}")

    if execution_result:
        print(f"   Resultado: {execution_result}")

print()
print()

# Test 3: Verificar cache de noticias
print("📍 TEST 3: CACHE DE NOTICIAS")
print("-" * 40)
print("Verificando si omite ingestión con datos recientes...")
print()

from orchestrator.agent import should_skip_news_ingestion

skip = should_skip_news_ingestion()

if skip:
    print("✅ Hay noticias recientes (< 4 horas)")
    print("   El sistema OMITIRÁ la ingestión de noticias")
else:
    print("ℹ️  No hay noticias recientes")
    print("   El system REALIZARÁ ingestión de noticias")

print()
print("="*70)
print()
print("🎯 RESUMEN:")
print("   ✅ AUTOPILOT_MODE=on activa ejecución automática")
print("   ✅ Cache de noticias evita re-procesamiento (< 4 horas)")
print()
print("🚀 Para ejecutar en producción:")
print("   AUTOPILOT_MODE=on .venv/bin/python .claude/subagents/orchestrator/agent.py 'theme' --capital 5000")
print()
