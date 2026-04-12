
import os
import sys
import json
from datetime import datetime

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from trading_mvp.analysis.quant_stats import fetch_historical_stats

def test_quant_indicators():
    tickers = ["BKR", "USO", "AAPL", "SPY"]
    print("="*70)
    print(f"🧪 TESTING 11 QUANTITATIVE INDICATORS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    for ticker in tickers:
        print(f"\n📊 Analyzing {ticker}...")
        stats = fetch_historical_stats(ticker)
        
        if "error" in stats:
            print(f"   ❌ Error: {stats['error']}")
            continue
            
        print(f"   Price: ${stats['current_price']} | Trend: {stats['trend']} | Momentum: {stats['momentum']}")
        
        print("\n   [I. STRUCTURE]")
        print(f"   - SMA 50: ${stats['sma_50']} | SMA 200: ${stats['sma_200']}")
        print(f"   - Distance to SMA 200: {stats['price_to_sma200_dist']}%")
        
        print("\n   [II. MOMENTUM]")
        print(f"   - RSI 14: {stats['rsi_14']}")
        print(f"   - MACD Hist: {stats['macd']['histogram']} (Line: {stats['macd']['line']} / Sig: {stats['macd']['signal']})")
        
        print("\n   [III. CONVICTION]")
        rvol = stats.get('rvol')
        rvol_str = f"{rvol}x" if rvol is not None else "N/A (insufficient data)"
        print(f"   - RVOL: {rvol_str} | OBV: {stats['obv']:,.0f}")
        
        print("\n   [IV. VOLATILITY]")
        atr = stats.get('atr_14')
        atr_str = f"${atr}" if atr is not None else "N/A"
        print(f"   - ATR 14: {atr_str} | Hist Vol (20d): {stats['std_dev_20']}%")
        
        print("\n   [V. SENSITIVITY]")
        beta = stats.get('beta_spy')
        corr = stats.get('corr_spy_20d')
        beta_str = f"{beta}" if beta is not None else "N/A"
        corr_str = f"{corr}" if corr is not None else "N/A"
        print(f"   - Beta (vs SPY): {beta_str} | Correlation 20d (vs SPY): {corr_str}")
        
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_quant_indicators()
