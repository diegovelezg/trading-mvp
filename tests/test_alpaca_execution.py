#!/usr/bin/env python3
"""
Test Alpaca Paper Trading Execution

Prueba la ejecución real de órdenes en Alpaca Paper Trading.

MODO DRY RUN (Testing - NO ejecuta):
    python test_alpaca_execution.py

MODO REAL (Ejecuta en Paper Trading):
    REAL_TRADING=true python test_alpaca_execution.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('alpaca_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up environment
os.environ['ALPACA_PAPER_API_KEY'] = 'YOUR_ALPACA_PAPER_API_KEY'
os.environ['PAPER_API_SECRET'] = 'YOUR_ALPACA_SECRET_KEY'
os.environ['SERPAPI_API_KEY'] = 'YOUR_SERPAPI_API_KEY'
os.environ['GEMINI_API_KEY'] = 'AIzaSyCutHRoCMkN02KhsVYATzu5XRPjboQZxnc'
os.environ['GEMINI_API_MODEL_01'] = 'gemini-3.1-flash-lite-preview'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.claude', 'subagents'))

print()
print("="*70)
print("💰 ALPACA PAPER TRADING - TEST DE EJECUCIÓN")
print("="*70)
print()

# Check mode
real_trading = os.getenv("REAL_TRADING", "false").lower() == "true"
mode_str = "✈️ REAL (Ejecuta órdenes)" if real_trading else "🧪 DRY RUN (Solo simula)"
print(f"Modo: {mode_str}")
print()

# Test Alpaca connection
print("1️⃣  VERIFICANDO CONEXIÓN CON ALPACA")
print("-" * 40)

try:
    from trading_mvp.execution.alpaca_orders import get_account, get_positions

    account = get_account()
    print(f"✅ Conexión exitosa")
    print(f"   Buying Power: ${account['buying_power']:.2f}")
    print(f"   Cash: ${account['cash']:.2f}")
    print(f"   Portfolio Value: ${account['portfolio_value']:.2f}")
    print()

    # Get current positions
    positions = get_positions()
    print(f"   Posiciones actuales: {len(positions)}")

    if positions:
        for pos in positions:
            print(f"      • {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f}")

    print()

except Exception as e:
    print(f"❌ Error conectando con Alpaca: {e}")
    print()
    print("🔧 Verifica que las credenciales estén configuradas:")
    print("   export ALPACA_PAPER_API_KEY='PKD...'")
    print("   export PAPER_API_SECRET='your_secret'")
    print()
    sys.exit(1)

# Test order execution (small test order)
print("2️⃣  TEST DE EJECUCIÓN DE ORDEN")
print("-" * 40)

# Use a small test position
test_ticker = "USO"  # Oil ETF (we have news for this)
test_position_size = 100.0  # Small amount for testing

try:
    from trading_mvp.agents.decision_agent import DecisionAgent, DecisionConfig

    # Create agent with test config
    if real_trading:
        config = DecisionConfig(
            autopilot_enabled=True,
            dry_run=False,  # REAL EXECUTION
            base_position_size=test_position_size
        )
    else:
        config = DecisionConfig(
            autopilot_enabled=True,
            dry_run=True,  # DRY RUN
            base_position_size=test_position_size
        )

    agent = DecisionAgent(config=config)

    print(f"Agente configurado:")
    print(f"   Autopilot: {config.autopilot_enabled}")
    print(f"   Dry Run: {config.dry_run}")
    print(f"   Position Size: ${test_position_size:.2f}")
    print()

    # Simulate a BULLISH recommendation for USO
    print(f"Simulando recomendación BULLISH para {test_ticker}...")

    mock_analysis = {
        'ticker': test_ticker,
        'recommendation': 'BULLISH',
        'avg_confidence': 0.85,
        'positive_ratio': 0.70,
        'negative_ratio': 0.25,
        'related_news_count': 14,
        'unique_entities_found': 38,
        'top_risks': [],
        'top_opportunities': [],
        'analysis_timestamp': '2026-04-08T14:15:00'
    }

    # Process recommendation
    decision = agent.analyze_recommendation(
        ticker_analysis=mock_analysis,
        portfolio_context={}
    )

    print()
    print("="*70)
    print("📊 RESULTADO DE LA DECISIÓN")
    print("="*70)
    print()

    print(f"Ticker: {decision['ticker']}")
    print(f"Recommendation: {decision['original_recommendation']}")
    print(f"Decision: {decision['decision']}")
    print(f"Action: {decision['action']}")
    print(f"Rationale: {decision['rationale']}")
    print()

    if decision['action'] == 'BOUGHT':
        print(f"💰 ORDEN DE COMPRA:")
        print(f"   Position Size: ${decision.get('position_size', 0):.2f}")
        print(f"   Entry Price: ${decision.get('entry_price', 0):.2f}")

        if decision.get('shares'):
            print(f"   Shares: {decision['shares']}")
        print(f"   Stop Loss: ${decision.get('stop_loss', 0):.2f}")
        print(f"   Take Profit: ${decision.get('take_profit', 0):.2f}")
        print()

        if decision.get('execution_status'):
            print(f"📊 ESTADO DE EJECUCIÓN:")
            print(f"   Status: {decision['execution_status']}")
            if decision['execution_status'] == 'SUCCESS':
                print(f"   Order ID: {decision.get('order_id')}")
                print(f"   Timestamp: {decision.get('execution_timestamp')}")
            else:
                print(f"   Error: {decision.get('execution_error', 'Unknown')}")
        else:
            if config.dry_run:
                print(f"🧪 DRY RUN MODE - Orden NO ejecutada")
            else:
                print(f"⚠️  Orden ejecutada (verificar en Alpaca)")

    print()
    print("="*70)
    print()
    print("🎯 PARA EJECUTAR EN PAPER TRADING REAL:")
    print("   REAL_TRADING=true python test_alpaca_execution.py")
    print()
    print("🎯 PARA VER POSICIONES EN ALPACA:")
    print("   Visita: https://alpaca.markets/paper/dashboard")
    print()

except Exception as e:
    print(f"❌ Error en test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
