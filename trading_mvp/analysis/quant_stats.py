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

def fetch_historical_stats(symbol: str, days: int = 365) -> Dict:
    """Fetch and calculate quantitative stats for a ticker.
    
    Returns:
        Dict with SMA, RSI, ATR, and Beta (vs SPY).
    """
    try:
        client = get_alpaca_data_client()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Fetch bars for the ticker and SPY (for beta)
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
        spy_df = df.xs("SPY").copy()

        # 1. Trend (SMA)
        ticker_df['sma_50'] = ticker_df['close'].rolling(window=50).mean()
        ticker_df['sma_200'] = ticker_df['close'].rolling(window=200).mean()
        
        current_price = ticker_df['close'].iloc[-1]
        sma_50 = ticker_df['sma_50'].iloc[-1]
        sma_200 = ticker_df['sma_200'].iloc[-1]
        
        trend = "BULLISH" if current_price > sma_200 else "BEARISH"
        momentum = "STRONG" if current_price > sma_50 else "WEAK"

        # 2. Volatility (ATR - 14 days)
        ticker_df['high_low'] = ticker_df['high'] - ticker_df['low']
        ticker_df['high_close'] = abs(ticker_df['high'] - ticker_df['close'].shift())
        ticker_df['low_close'] = abs(ticker_df['low'] - ticker_df['close'].shift())
        ticker_df['tr'] = ticker_df[['high_low', 'high_close', 'low_close']].max(axis=1)
        atr = ticker_df['tr'].rolling(window=14).mean().iloc[-1]

        # 3. Relative Strength (RSI - 14 days)
        delta = ticker_df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        # 4. Market Correlation (Beta vs SPY - 90 days)
        recent_ticker = ticker_df['close'].pct_change().iloc[-90:]
        recent_spy = spy_df['close'].pct_change().iloc[-90:]
        
        # Align indices
        combined = pd.concat([recent_ticker, recent_spy], axis=1).dropna()
        if len(combined) > 10:
            covariance = combined.cov().iloc[0, 1]
            variance = combined.iloc[:, 1].var()
            beta = covariance / variance
        else:
            beta = 1.0

        return {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "trend": trend,
            "momentum": momentum,
            "sma_50": round(sma_50, 2) if not np.isnan(sma_50) else None,
            "sma_200": round(sma_200, 2) if not np.isnan(sma_200) else None,
            "rsi_14": round(rsi, 2) if not np.isnan(rsi) else 50.0,
            "atr_14": round(atr, 2) if not np.isnan(atr) else 0.0,
            "beta_spy": round(beta, 2),
            "volatility_ratio": round((atr / current_price) * 100, 2) # % of price
        }

    except Exception as e:
        logger.error(f"Error calculating quant stats for {symbol}: {e}")
        return {"error": str(e)}
