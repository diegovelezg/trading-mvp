#!/usr/bin/env python3
"""Test del sistema completo de trading (SIN ejecución real)."""

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
print("🚀 SISTEMA DE TRADING COMPLETO - TEST")
print("="*70)
print()
print("✅ Sistema implementado:")
print("   1. Explorer Agent - Descubre tickers por tema")
print("   2. Macro Analyst - Analiza sentimiento de mercado")
print("   3. Bull/Bear/Risk Agents - Análisis en paralelo")
print("   4. CIO Agent - Decisión estratégica final")
print("   5. Portfolio Logic - Guardrails deterministas")
print("   6. Executioner - Ejecución en Alpaca Paper Trading")
print()
print("📊 Flujo completo:")
print("   Tema → Discovery → Sentiment → Mesa → CIO → Execution")
print()

# Importar orchestrator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.claude', 'subagents'))
from orchestrator.agent import orchestrate_investment_workflow

print("🎯 Probando con tema: 'cloud computing'")
print("   Capital: $5,000")
print()

try:
    result = orchestrate_investment_workflow(
        theme="cloud computing",
        capital=5000.0,
        execute=False  # NO ejecutar orden real (solo análisis)
    )

    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        sys.exit(1)

    print()
    print("="*70)
    print("📊 RESULTADO DEL SISTEMA")
    print("="*70)
    print()

    # CIO Decision
    cio_decision = result.get('cio_decision', {})
    print("🧠 DECISIÓN DEL CIO:")
    print(f"   Ticker: {cio_decision.get('selected_ticker')}")
    print(f"   Action: {cio_decision.get('action')}")
    print(f"   Target Size: ${cio_decision.get('target_size_usd', 0):.2f}")

    if 'guardrail_check' in cio_decision:
        guardrail = cio_decision['guardrail_check']
        print(f"   Guardrail Check: {guardrail.get('is_valid')}")
        print(f"   Allowed Size: ${guardrail.get('allowed_size_usd', 0):.2f}")
        print(f"   Reason: {guardrail.get('reason')}")

    print()
    print(f"💡 Rationale del CIO:")
    rationale = cio_decision.get('rationale', 'N/A')
    print(f"   {rationale[:300]}...")
    print()

    # Portfolio State
    portfolio_state = result.get('portfolio_state', {})
    print()
    print("💰 ESTADO DE PORTFOLIO:")
    print(f"   Equity: ${portfolio_state.get('equity', 0):,.2f}")
    print(f"   Cash: ${portfolio_state.get('cash', 0):,.2f}")
    print(f"   Exposure: ${portfolio_state.get('total_exposure_usd', 0):,.2f}")
    print(f"   Exposure %: {portfolio_state.get('total_exposure_pct', 0)*100:.1f}%")
    print(f"   Num Positions: {portfolio_state.get('num_positions', 0)}")
    print()

    # Prioritization List
    prioritization = cio_decision.get('prioritization_list', [])
    if prioritization:
        print("📊 PRIORIZACIÓN DEL CIO:")
        for i, item in enumerate(prioritization, 1):
            ticker = item.get('ticker', 'N/A')
            rank = item.get('rank', 'N/A')
            score = item.get('score', 'N/A')
            print(f"   {i}. {ticker} - Rank: {rank} | Score: {score}")
        print()

    print("="*70)
    print()
    print("✅ SISTEMA COMPLETO FUNCIONANDO")
    print()
    print("🚀 Para ejecutar una orden REAL en Alpaca Paper Trading:")
    print("   .venv/bin/python .claude/subagents/orchestrator/agent.py 'cloud computing' --capital 5000 --execute")
    print()
    print("🎯 Otros temas para probar:")
    print("   'AI infrastructure'")
    print("   'electric vehicles'")
    print("   'renewable energy'")
    print("   'semiconductor stocks'")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
