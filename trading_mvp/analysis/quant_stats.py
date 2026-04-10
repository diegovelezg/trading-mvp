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
    """Fetch and calculate quantitative stats for a ticker using Wilder's Smoothing (Gold Standard).
    
    Returns:
        Dict with SMA, RSI, ATR, and Beta (vs SPY).
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

        # 1. Trend (Standard SMA)
        ticker_df['sma_50'] = ticker_df['close'].rolling(window=min(50, len(ticker_df))).mean()
        ticker_df['sma_200'] = ticker_df['close'].rolling(window=min(200, len(ticker_df))).mean()
        
        current_price = ticker_df['close'].iloc[-1]
        sma_50 = ticker_df['sma_50'].iloc[-1]
        
        if len(ticker_df) >= 200:
            sma_200 = ticker_df['sma_200'].iloc[-1]
            trend = "BULLISH" if current_price > sma_200 else "BEARISH"
        else:
            sma_200 = 0.0
            trend = "NEUTRAL (Insufficient history for SMA 200)"

        momentum = "POSITIVE" if current_price > sma_50 else "NEGATIVE"

        # 2. RSI (Relative Strength Index) - Wilder's Smoothing Standard
        delta = ticker_df['close'].diff()
        gain = (delta.where(delta > 0, 0))
        loss = (-delta.where(delta < 0, 0))
        
        # Wilder's Smoothing = EMA with alpha = 1/N
        avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        
        rs = avg_gain / avg_loss.replace(0, 0.001)
        ticker_df['rsi_14'] = 100 - (100 / (1 + rs))
        rsi_14 = ticker_df['rsi_14'].iloc[-1]
        
        if np.isnan(rsi_14): rsi_14 = 50.0

        # 3. ATR (Average True Range) - Wilder's Smoothing Standard
        ticker_df['h_l'] = ticker_df['high'] - ticker_df['low']
        ticker_df['h_pc'] = abs(ticker_df['high'] - ticker_df['close'].shift(1))
        ticker_df['l_pc'] = abs(ticker_df['low'] - ticker_df['close'].shift(1))
        ticker_df['tr'] = ticker_df[['h_l', 'h_pc', 'l_pc']].max(axis=1)
        
        # Wilder's ATR uses the same 1/N smoothing
        ticker_df['atr_14'] = ticker_df['tr'].ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        atr = ticker_df['atr_14'].iloc[-1]
        
        if np.isnan(atr): atr = 0.0

        # 4. Beta (Correlation with SPY)
        beta_spy = 1.0
        if "SPY" in df.index.get_level_values(0):
            spy_df = df.xs("SPY").copy()
            ticker_returns = ticker_df['close'].pct_change()
            spy_returns = spy_df['close'].pct_change()
            combined = pd.concat([ticker_returns, spy_returns], axis=1).dropna()
            combined.columns = ['ticker', 'spy']
            if len(combined) > 30:
                covariance = combined.cov().iloc[0, 1]
                variance = combined['spy'].var()
                if variance > 0:
                    beta_spy = round(covariance / variance, 2)

        return {
            "current_price": round(float(current_price), 2),
            "sma_50": round(float(sma_50), 2) if not np.isnan(sma_50) else 0,
            "sma_200": round(float(sma_200), 2) if not np.isnan(sma_200) else 0,
            "trend": trend,
            "momentum": momentum,
            "rsi_14": round(float(rsi_14), 1),
            "atr_14": round(float(atr), 2),
            "volatility_ratio": round((atr / current_price) * 100, 2) if current_price > 0 else 0,
            "beta_spy": beta_spy
        }

    except Exception as e:
        logger.error(f"Error calculating quant stats for {symbol}: {e}")
        return {"error": str(e)}
