"""Validar Quant Stats + CIO con los mismos tickers que fallaron"""
import os
import sys
import json
from trading_mvp.analysis.quant_stats import fetch_historical_stats
from dotenv import load_dotenv
import openai

load_dotenv()

print("🔍 VALIDANDO QUANT STATS (Bug corregido)")
print("=" * 60)

tickers = ['BWXT', 'DNN', 'UEC']
quant_results = []

for ticker in tickers:
    result = fetch_historical_stats(ticker)
    if 'error' in result:
        print(f"❌ {ticker}: {result['error']}")
    else:
        print(f"✅ {ticker}: ${result.get('current_price')} | Trend: {result.get('trend')} | RSI: {result.get('rsi_14')} | Beta: {result.get('beta_spy')}")
        quant_results.append({
            'ticker': ticker,
            'quant_stats': result
        })

print("\n🧠 VALIDANDO CIO (Endpoint corregido)")
print("=" * 60)

# Mock data para el CIO
tickers_analysis = [
    {
        'ticker': 'BWXT',
        'quant_stats': quant_results[0]['quant_stats'],
        'sentiment_score': 0.3,
        'bull_case': {'overall_sentiment': 'Strong Buy - Nuclear energy demand surge'},
        'bear_case': {'overall_sentiment': 'Sell - Regulatory risks'},
        'risk_analysis': {'risk_score': 'Medium'}
    }
]

portfolio_state = {
    'equity': 100000.08,
    'cash': 99875.74,
    'exposure_pct': 0.1
}

portfolio_metrics = {
    'sharpe_ratio': 1.5,
    'win_rate': 65.0
}

strategy_metrics = {
    'total_trades': 10,
    'winning_trades': 6
}

sys.path.insert(0, '.claude/subagents')
from cio.agent import make_investment_decision
decision = make_investment_decision(tickers_analysis, portfolio_state, portfolio_metrics, strategy_metrics)

print(f"\n🎯 DECISIÓN DEL CIO:")
print(f"   Ticker: {decision.get('selected_ticker')}")
print(f"   Action: {decision.get('action')}")
print(f"   Target Size: ${decision.get('target_size_usd', 0):,.2f}")
print(f"   Rationale: {decision.get('rationale', 'N/A')[:100]}...")

print("\n✅ VALIDACIÓN COMPLETADA")
