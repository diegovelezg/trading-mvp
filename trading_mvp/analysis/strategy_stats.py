"""Strategy Performance Metrics (Win Rate, Gain-to-Pain, Omega)."""

import sqlite3
import logging
import pandas as pd
import numpy as np
from typing import Dict
from trading_mvp.core.db_manager import get_connection

logger = logging.getLogger(__name__)

def calculate_strategy_stats() -> Dict:
    """Analyze the trading history from the database to get professional strategy metrics."""
    try:
        conn = get_connection()
        # Query investment_decisions where status is CLOSED
        df = pd.read_sql_query("""
            SELECT profit_loss, profit_loss_pct, execution_timestamp, exit_timestamp
            FROM investment_decisions 
            WHERE status = 'CLOSED' AND profit_loss IS NOT NULL
        """, conn)
        conn.close()

        if df.empty or len(df) < 3:
            return {"error": "Insufficient closed trades for strategy analysis"}

        pl = df['profit_loss'].values
        
        # 1. Win Rate
        wins = pl[pl > 0]
        win_rate = len(wins) / len(pl)

        # 2. Gain-to-Pain Ratio (Total Gains / Abs(Total Losses))
        losses = pl[pl < 0]
        total_gains = np.sum(wins)
        total_losses = np.abs(np.sum(losses)) if len(losses) > 0 else 0
        gain_to_pain = total_gains / total_losses if total_losses != 0 else 0

        # 3. Profit Factor
        profit_factor = total_gains / total_losses if total_losses != 0 else 100 # Default if no losses

        # 4. Omega Ratio (Simplified: Gain vs Loss Threshold)
        # Assuming 0 as threshold
        omega = total_gains / total_losses if total_losses != 0 else 2.99 # Mock top-tier if no loss

        # 5. Average Win vs Average Loss (Risk/Reward realized)
        avg_win = np.mean(wins) if len(wins) > 0 else 0
        avg_loss = np.abs(np.mean(losses)) if len(losses) > 0 else 0
        realized_rr = avg_win / avg_loss if avg_loss != 0 else 1.0

        return {
            "win_rate": round(win_rate * 100, 2),
            "gain_to_pain": round(float(gain_to_pain), 2),
            "profit_factor": round(float(profit_factor), 2),
            "omega_ratio": round(float(omega), 2),
            "realized_rr": round(float(realized_rr), 2),
            "total_trades": len(pl)
        }

    except Exception as e:
        logger.error(f"Error calculating strategy stats: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    stats = calculate_strategy_stats()
    print(f"Strategy Stats: {stats}")
