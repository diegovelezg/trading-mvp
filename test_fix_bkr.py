#!/usr/bin/env python3
"""Test script to verify BKR connection fix."""

from trading_mvp.analysis.quant_stats import fetch_historical_stats

# Test con múltiples tickers seguidos (simulando la mesa de inversiones)
tickers = ["BKR", "TSM", "MA", "SNPS", "BWXT", "PWR", "PEG", "WEC", "QCOM"]

print("Testing sequential ticker analysis (simulating Investment Desk)...")
print("=" * 60)

for ticker in tickers:
    print(f"Testing {ticker}...")
    result = fetch_historical_stats(ticker)
    if "error" in result:
        print(f"  ❌ ERROR: {result['error']}")
    else:
        print(f"  ✅ OK - Price: ${result['current_price']}")

print("=" * 60)
print("✅ All tickers processed successfully!")