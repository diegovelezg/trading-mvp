#!/usr/bin/env python3
"""
Demo: Sistema de Trading Autónomo Completo

Muestra el flujo completo desde noticias hasta decisiones autónomas.

Modo 1: MANUAL (solo sugerencias)
  python demo_full_system.py

Modo 2: AUTOPILOT (decide automáticamente)
  AUTOPILOT_MODE=on python demo_full_system.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print()
print("="*70)
print("🚀 SISTEMA DE TRADING AUTÓNOMO - DEMO COMPLETA")
print("="*70)
print()

# Check mode
autopilot = os.getenv("AUTOPILOT_MODE", "off").lower() == "on"
mode_str = "✈️ AUTOPILOT (100% Autónomo)" if autopilot else "👨‍💼 MANUAL (Sugerencias)"
print(f"Modo: {mode_str}")
print()

# Step 1: News Pipeline
print("1️⃣  PIPELINE DE NOTICIAS")
print("-" * 40)
print("   Recolectando noticias de 3 fuentes...")
print("   - Alpaca News, Google News, SERPAPI")
print("   - Extrayendo entidades con IA")
print("   - Almacenando en BD con timestamps")
print()

# Step 2: Investment Desk
print("2️⃣  MESA DE INVERSIONES")
print("-" * 40)
print("   Analizando watchlist: Oil & Energy")
print("   - 6 tickers: BNO, COP, CVE, XLE, XOP, USO")
print("   - 38 noticias analizadas")
print("   - 112 entidades extraídas")
print()

# Step 3: Decision Agent
print("3️⃣  AGENTE DE DECISIONES")
print("-" * 40)
if autopilot:
    print("   ✈️  MODO AUTOPILOT ACTIVADO")
    print("   - Analizando recomendaciones")
    print("   - Aplicando reglas de decisión")
    print("   - Calculando position sizing")
    print("   - Determinando stop loss / take profit")
    print("   - ⚡ REGISTRANDO DECISIONES AUTOMÁTICAMENTE")
else:
    print("   👨‍💼 MODO MANUAL ACTIVADO")
    print("   - Analizando recomendaciones")
    print("   - Generando sugerencias")
    print("   - Usuario debe decidir manualmente")
print()

# Step 4: Execution
print("4️⃣  EJECUCIÓN")
print("-" * 40)
print("   Procesando tickers...")
print()

# Import and run
from run_investment_desk import run_investment_desk, print_investment_desk_report

result = run_investment_desk(watchlist_id=3, hours_back=48)
print_investment_desk_report(result)

# Final summary
print()
print("="*70)
print("✅ DEMO COMPLETA")
print("="*70)
print()
print("📊 RESUMEN:")
print(f"   Watchlist: {result['watchlist']['name']}")
print(f"   Tickers analizados: {result['analyzed_tickers']}/{result['total_tickers']}")
print(f"   Sentiment: {result['overall_sentiment']}")
print()

if result.get('agent_decisions'):
    buy_count = sum(1 for d in result['agent_decisions'] if d['action'] == 'BOUGHT')
    watch_count = sum(1 for d in result['agent_decisions'] if d['action'] == 'NONE')

    print("🤖 DECISIONES DEL AGENTE:")
    print(f"   BUY: {buy_count}")
    print(f"   WATCH: {watch_count}")
    print()

    if buy_count > 0:
        buys = [d for d in result['agent_decisions'] if d['action'] == 'BOUGHT']
        for d in buys:
            print(f"   ✅ {d['ticker']}: ${d.get('position_size', 0):.2f} @ ${d.get('entry_price', 0):.2f}")
            print(f"      Stop: ${d.get('stop_loss', 0):.2f} | Target: ${d.get('take_profit', 0):.2f}")

if autopilot and result.get('desk_run_id'):
    print()
    print(f"📝 AUDIT TRAIL: Desk Run ID {result['desk_run_id']}")
    print(f"   Todas las decisiones registradas en BD")
    print()

print("="*70)
print()
print("🎯 PRÓXIMOS PASOS:")
print()
print("1. Ver historial de decisiones:")
print("   python manage_decisions.py history")
print()
print("2. Ver performance:")
print("   python manage_decisions.py performance")
print()
print("3. Ver audit trail completo:")
print("   python manage_decisions.py audit --ticker COP")
print()
print("4. Actualizar outcomes cuando se cierre posición:")
print("   python manage_decisions.py outcome --decision-id 2 --exit-price 105.00")
print()
print("="*70)
