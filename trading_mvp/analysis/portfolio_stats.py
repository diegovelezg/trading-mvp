"""Advanced Portfolio Performance Metrics (Sharpe, Sortino, Calmar, VaR)."""

import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetPortfolioHistoryRequest
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def get_trading_client() -> TradingClient:
    api_key = os.getenv("ALPACA_PAPER_API_KEY")
    secret_key = os.getenv("PAPER_API_SECRET")
    return TradingClient(api_key, secret_key, paper=True)

def calculate_portfolio_metrics(period: str = "1M", timeframe: str = "1D") -> Dict:
    """Calculate professional-grade metrics from Alpaca portfolio history."""
    try:
        client = get_trading_client()
        
        # Fetch portfolio history
        history = client.get_portfolio_history(GetPortfolioHistoryRequest(
            period=period,
            timeframe=timeframe
        ))
        
        # Convert to DataFrame
        df = pd.DataFrame({
            'equity': history.equity,
            'timestamp': history.timestamp
        })
        df = df.dropna()
        
        if df.empty or len(df) < 2:
            return {"error": "Insufficient history for metrics"}

        # Returns
        df['returns'] = df['equity'].pct_change().dropna()
        returns = df['returns'].values
        
        # 1. Sharpe Ratio (Annualized, assuming 0.02 risk-free rate)
        rf_daily = (1 + 0.02)**(1/252) - 1
        excess_returns = returns - rf_daily
        sharpe = np.sqrt(252) * np.mean(excess_returns) / np.std(returns) if np.std(returns) != 0 else 0

        # 2. Sortino Ratio (Downside deviation only)
        downside_returns = returns[returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
        sortino = np.sqrt(252) * np.mean(excess_returns) / downside_std if downside_std != 0 else 0

        # 3. Max Drawdown & Calmar Ratio
        df['peak'] = df['equity'].cummax()
        df['drawdown'] = (df['equity'] - df['peak']) / df['peak']
        max_drawdown = df['drawdown'].min()
        
        annual_return = (df['equity'].iloc[-1] / df['equity'].iloc[0]) - 1
        calmar = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0

        # 4. Value at Risk (VaR 95%)
        var_95 = np.percentile(returns, 5)

        # 5. Ulcer Index (Stress Measure)
        ulcer_index = np.sqrt(np.mean(df['drawdown']**2)) * 100

        return {
            "sharpe_ratio": round(float(sharpe), 2),
            "sortino_ratio": round(float(sortino), 2),
            "calmar_ratio": round(float(calmar), 2),
            "max_drawdown": round(float(max_drawdown) * 100, 2),
            "var_95_daily": round(float(var_95) * 100, 2),
            "ulcer_index": round(float(ulcer_index), 2),
            "total_return_period": round(float(annual_return) * 100, 2)
        }

    except Exception as e:
        logger.error(f"Error calculating portfolio metrics: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    stats = calculate_portfolio_metrics()
    print(f"Portfolio Stats: {stats}")
