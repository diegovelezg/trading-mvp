"""Ejecutar MESA ANALYSIS completo para NXE (sin noticias)"""
import sys
import os
sys.path.insert(0, '.claude/subagents')

from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("🔍 MESA ANALYSIS COMPLETO - NXE (NexGen Energy)")
print("=" * 70)

# Importar agentes necesarios
from bull_researcher.agent import analyze_bull_case
from bear_researcher.agent import analyze_bear_case
from risk_manager.agent import assess_risk
from trading_mvp.analysis.quant_stats import fetch_historical_stats

ticker = "NXE"
capital = 3000

print(f"\n📊 Ticker: {ticker}")
print(f"💰 Capital Referencia: ${capital:,.2f}")

# STEP 1: QUANT STATS
print("\n" + "=" * 70)
print("📈 STEP 1: ANÁLISIS CUANTITATIVO")
print("=" * 70)

quant_stats = fetch_historical_stats(ticker)
if 'error' in quant_stats:
    print(f"❌ Error: {quant_stats['error']}")
    exit(1)

print(f"   Precio Actual: ${quant_stats.get('current_price')}")
print(f"   Trend: {quant_stats.get('trend')}")
print(f"   Momentum: {quant_stats.get('momentum')}")
print(f"   SMA 50: ${quant_stats.get('sma_50')}")
print(f"   SMA 200: ${quant_stats.get('sma_200')}")
print(f"   RSI (14): {quant_stats.get('rsi_14')}")
print(f"   ATR (14): ${quant_stats.get('atr_14')}")
print(f"   Beta vs SPY: {quant_stats.get('beta_spy')}")
print(f"   Volatility Ratio: {quant_stats.get('volatility_ratio')}%")

# STEP 2: BULL CASE
print("\n" + "=" * 70)
print("📈 STEP 2: BULL RESEARCHER (Argumentos Alcistas)")
print("=" * 70)

bull_case = analyze_bull_case(ticker)
print(f"   Sentimiento General: {bull_case.get('overall_sentiment')}")
print(f"   Convicción: {bull_case.get('conviction_level')}")

# Argumentos pueden venir como dict o str
arguments = bull_case.get('arguments', [])
print(f"\n   Argumentos Clave:")
for i, arg in enumerate(arguments[:3], 1):
    if isinstance(arg, dict):
        print(f"   {i}. {arg.get('title')}")
        print(f"      {arg.get('description', '')[:80]}...")
    else:
        print(f"   {i}. {str(arg)[:100]}")

# STEP 3: BEAR CASE
print("\n" + "=" * 70)
print("📉 STEP 3: BEAR RESEARCHER (Argumentos Bajistas)")
print("=" * 70)

bear_case = analyze_bear_case(ticker)
print(f"   Sentimiento General: {bear_case.get('overall_sentiment')}")
print(f"   Riesgo Principal: {bear_case.get('primary_risk')}")

# Argumentos pueden venir como dict o str
arguments = bear_case.get('arguments', [])
print(f"\n   Argumentos Clave:")
for i, arg in enumerate(arguments[:3], 1):
    if isinstance(arg, dict):
        print(f"   {i}. {arg.get('title')}")
        print(f"      {arg.get('description', '')[:80]}...")
    else:
        print(f"   {i}. {str(arg)[:100]}")

# STEP 4: RISK MANAGER
print("\n" + "=" * 70)
print("⚡ STEP 4: RISK MANAGER (Evaluación de Riesgo)")
print("=" * 70)

risk_analysis = assess_risk(ticker, capital)
print(f"   Nivel de Riesgo: {risk_analysis.get('risk_score')}")
print(f"   Tamaño Posición Máximo: ${risk_analysis.get('max_position_size') or 'N/A'}")
print(f"   Stop Loss: ${risk_analysis.get('stop_loss') or 'N/A'}")
print(f"   Distancia Stop Loss: {risk_analysis.get('stop_distance_pct') or 'N/A'}%")
print(f"   Ratio Riesgo/Retorno: {risk_analysis.get('risk_reward_ratio') or 'N/A'}")

# RESUMEN EJECUTIVO
print("\n" + "=" * 70)
print("🎯 RESUMEN EJECUTIVO - NXE")
print("=" * 70)

# Determinar acción basada en análisis
trend = quant_stats.get('trend')
rsi = quant_stats.get('rsi_14')
risk_level = risk_analysis.get('risk_score')
bull_sentiment = bull_case.get('overall_sentiment', '').lower()
bear_sentiment = bear_case.get('overall_sentiment', '').lower()

accion = "HOLD"
if trend == "BULLISH" and rsi < 70 and risk_level in ["Low", "Medium"]:
    if "buy" in bull_sentiment or "strong" in bull_sentiment:
        accion = "BUY"
elif trend == "BEARISH" or rsi > 70:
    if "sell" in bear_sentiment or "strong" in bear_sentiment:
        accion = "SELL"

print(f"   📊 Trend Técnico: {trend}")
print(f"   📈 RSI: {rsi} ({'Sobrecomprado' if rsi > 70 else 'Sobrevendido' if rsi < 30 else 'Neutral'})")
print(f"   ⚡ Nivel Riesgo: {risk_level}")
print(f"   🐂 Bull Case: {bull_case.get('overall_sentiment')}")
print(f"   🐻 Bear Case: {bear_case.get('overall_sentiment')}")
print(f"\n   🎯 RECOMENDACIÓN: {accion}")

# Calcular tamaño basado en riesgo si no está disponible
max_size = risk_analysis.get('max_position_size')
if not max_size:
    # Usar ATR-based sizing
    atr = quant_stats.get('atr_14', 1)
    price = quant_stats.get('current_price', 1)
    risk_per_share = atr * 2  # 2x ATR risk
    if risk_per_share > 0:
        max_size = (capital * 0.02) / (risk_per_share / price)  # 2% risk rule
    else:
        max_size = capital * 0.1  # Default 10%

print(f"   💵 Tamaño Sugerido: ${float(max_size) if max_size else 0:,.2f}")

print("\n" + "=" * 70)
print("✅ MESA ANALYSIS COMPLETADO")
print("=" * 70)
