"""Quantitative analysis tools for tickers using Alpaca historical data."""

import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def get_alpaca_data_client() -> StockHistoricalDataClient:
    """Get authenticated Alpaca data client."""
    api_key = os.getenv("ALPACA_PAPER_API_KEY")
    secret_key = os.getenv("PAPER_API_SECRET")
    return StockHistoricalDataClient(api_key, secret_key)

def fetch_historical_stats(symbol: str, days: int = 400) -> Dict:
    """Fetch and calculate 11 quantitative indicators for a ticker.
    
    Dimensions:
    I. Structure: SMA 50, SMA 200, Price vs SMA Distance (%)
    II. Momentum: RSI 14, MACD (Line, Signal, Histogram)
    III. Conviction: RVOL (Relative Volume), OBV (On-Balance Volume)
    IV. Volatilidad: ATR 14, Std Dev (20d)
    V. Sensibilidad: Beta (vs SPY), Correlation (vs SPY)
    """
    try:
        client = get_alpaca_data_client()
        
        # Use yesterday as end_date to ensure consolidated historical data
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=days)

        request_params = StockBarsRequest(
            symbol_or_symbols=[symbol, "SPY"],
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date
        )
        
        bars = client.get_stock_bars(request_params)
        df = bars.df
        
        if df.empty or symbol not in df.index.get_level_values(0):
            return {"error": f"No data found for {symbol}"}

        # Isolate ticker data
        ticker_df = df.xs(symbol).copy()
        
        if len(ticker_df) < 30:
            return {"error": f"Insufficient data history for {symbol} (need at least 30 days)"}

        # --- I. STRUCTURE ---
        ticker_df['sma_50'] = ticker_df['close'].rolling(window=min(50, len(ticker_df))).mean()
        ticker_df['sma_200'] = ticker_df['close'].rolling(window=min(200, len(ticker_df))).mean()
        
        current_price = float(ticker_df['close'].iloc[-1])
        sma_50 = float(ticker_df['sma_50'].iloc[-1])
        sma_200 = float(ticker_df['sma_200'].iloc[-1]) if not np.isnan(ticker_df['sma_200'].iloc[-1]) else 0.0
        
        price_to_sma200_dist = ((current_price / sma_200) - 1) * 100 if sma_200 > 0 else 0.0
        trend = "BULLISH" if (sma_200 > 0 and current_price > sma_200) else "BEARISH"
        momentum_dir = "POSITIVE" if current_price > sma_50 else "NEGATIVE"

        # --- II. MOMENTUM ---
        # RSI 14 (Wilder's Smoothing)
        delta = ticker_df['close'].diff()
        gain = (delta.where(delta > 0, 0))
        loss = (-delta.where(delta < 0, 0))
        avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, 0.001)
        ticker_df['rsi_14'] = 100 - (100 / (1 + rs))
        rsi_14 = float(ticker_df['rsi_14'].iloc[-1])

        # MACD (12, 26, 9)
        exp1 = ticker_df['close'].ewm(span=12, adjust=False).mean()
        exp2 = ticker_df['close'].ewm(span=26, adjust=False).mean()
        ticker_df['macd_line'] = exp1 - exp2
        ticker_df['macd_signal'] = ticker_df['macd_line'].ewm(span=9, adjust=False).mean()
        ticker_df['macd_hist'] = ticker_df['macd_line'] - ticker_df['macd_signal']
        
        macd_val = float(ticker_df['macd_line'].iloc[-1])
        macd_signal = float(ticker_df['macd_signal'].iloc[-1])
        macd_hist = float(ticker_df['macd_hist'].iloc[-1])

        # --- III. CONVICTION ---
        # RVOL (Relative Volume vs 20d Avg)
        avg_vol_20 = ticker_df['volume'].rolling(window=20).mean()
        current_vol = ticker_df['volume'].iloc[-1]
        rvol = float(current_vol / avg_vol_20.iloc[-1]) if avg_vol_20.iloc[-1] > 0 else 1.0

        # OBV (On-Balance Volume)
        obv = (np.sign(ticker_df['close'].diff()) * ticker_df['volume']).fillna(0).cumsum()
        current_obv = float(obv.iloc[-1])

        # --- IV. VOLATILITY ---
        # ATR 14
        ticker_df['h_l'] = ticker_df['high'] - ticker_df['low']
        ticker_df['h_pc'] = abs(ticker_df['high'] - ticker_df['close'].shift(1))
        ticker_df['l_pc'] = abs(ticker_df['low'] - ticker_df['close'].shift(1))
        ticker_df['tr'] = ticker_df[['h_l', 'h_pc', 'l_pc']].max(axis=1)
        ticker_df['atr_14'] = ticker_df['tr'].ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        atr_14 = float(ticker_df['atr_14'].iloc[-1])
        
        # Standard Deviation (20d)
        std_dev_20 = float(ticker_df['close'].rolling(window=20).std().iloc[-1])

        # --- V. SENSITIVITY ---
        beta_spy = 1.0
        corr_spy = 1.0
        
        if "SPY" in df.index.get_level_values(0):
            spy_df = df.xs("SPY").copy()
            ticker_returns = ticker_df['close'].pct_change()
            spy_returns = spy_df['close'].pct_change()
            combined = pd.concat([ticker_returns, spy_returns], axis=1).dropna()
            combined.columns = ['ticker', 'spy']
            
            if len(combined) > 30:
                # Beta
                covariance = combined.cov().iloc[0, 1]
                variance = combined['spy'].var()
                if variance > 0:
                    beta_spy = round(float(covariance / variance), 2)
                
                # Correlation (Rolling 20d last value)
                corr_spy = round(float(combined['ticker'].rolling(window=20).corr(combined['spy']).iloc[-1]), 2)

        return {
            "current_price": round(current_price, 2),
            "sma_50": round(sma_50, 2),
            "sma_200": round(sma_200, 2),
            "price_to_sma200_dist": round(price_to_sma200_dist, 2),
            "trend": trend,
            "momentum": momentum_dir,
            "rsi_14": round(rsi_14, 1),
            "macd": {
                "line": round(macd_val, 3),
                "signal": round(macd_signal, 3),
                "histogram": round(macd_hist, 3)
            },
            "rvol": round(rvol, 2),
            "obv": round(current_obv, 0),
            "atr_14": round(atr_14, 2),
            "std_dev_20": round(std_dev_20, 2),
            "volatility_ratio": round((atr_14 / current_price) * 100, 2) if current_price > 0 else 0,
            "beta_spy": beta_spy,
            "corr_spy": corr_spy
        }

    except Exception as e:
        logger.error(f"Error calculating quant stats for {symbol}: {e}")
        return {"error": str(e)}

    except Exception as e:
        logger.error(f"Error calculating quant stats for {symbol}: {e}")
        return {"error": str(e)}
