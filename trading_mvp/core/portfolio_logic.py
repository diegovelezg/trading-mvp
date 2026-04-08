"""Portfolio management logic and deterministic guardrails."""

import logging
from typing import Dict, List, Tuple
from trading_mvp.execution.alpaca_orders import get_account, get_positions

logger = logging.getLogger(__name__)

# Portfolio Rules (Constants)
MAX_TICKER_EXPOSURE_PCT = 0.15  # Max 15% of equity per ticker
MAX_TOTAL_EXPOSURE_PCT = 0.80   # Max 80% total exposure
MIN_CASH_RESERVE_PCT = 0.10     # Keep 10% in cash
MAX_POSITION_SIZE_USD = 5000.0  # Absolute max per trade for safety in MVP

def validate_trade_size(symbol: str, requested_size_usd: float) -> Tuple[bool, float, str]:
    """Validate if a trade size is acceptable according to portfolio rules.

    Args:
        symbol: Ticker symbol
        requested_size_usd: Proposed investment amount

    Returns:
        (is_valid, allowed_size_usd, reason)
    """
    try:
        account = get_account()
        positions = get_positions()

        equity = account['equity']
        cash = account['cash']
        total_value = account['portfolio_value']

        # 1. Check absolute safety limit
        allowed_size = min(requested_size_usd, MAX_POSITION_SIZE_USD)

        # 2. Check individual ticker exposure
        current_pos = next((p for p in positions if p['symbol'] == symbol), None)
        current_exposure = 0.0
        if current_pos:
            current_exposure = float(current_pos['qty']) * float(current_pos['current_price'])

        max_allowed_ticker = equity * MAX_TICKER_EXPOSURE_PCT
        remaining_ticker_room = max_allowed_ticker - current_exposure

        if remaining_ticker_room <= 0:
            return False, 0.0, f"Max exposure for {symbol} reached ({MAX_TICKER_EXPOSURE_PCT*100}%)"

        allowed_size = min(allowed_size, remaining_ticker_room)

        # 3. Check total portfolio exposure
        total_exposure = total_value - cash
        max_total_exposure = equity * MAX_TOTAL_EXPOSURE_PCT
        remaining_total_room = max_total_exposure - total_exposure

        if remaining_total_room <= 0:
            return False, 0.0, f"Max total portfolio exposure reached ({MAX_TOTAL_EXPOSURE_PCT*100}%)"

        allowed_size = min(allowed_size, remaining_total_room)

        # 4. Check cash availability (with reserve)
        available_cash = cash - (equity * MIN_CASH_RESERVE_PCT)
        if available_cash <= 0:
            return False, 0.0, f"Insufficient cash reserve (Min {MIN_CASH_RESERVE_PCT*100}% required)"

        allowed_size = min(allowed_size, available_cash)

        if allowed_size < requested_size_usd:
            reason = f"Size reduced from ${requested_size_usd:,.2f} to ${allowed_size:,.2f} due to risk rules"
            return True, allowed_size, reason

        return True, requested_size_usd, "Valid trade size"

    except Exception as e:
        logger.error(f"Error validating trade size: {e}")
        return False, 0.0, f"Error in portfolio logic: {str(e)}"

def get_portfolio_health() -> Dict:
    """Get a summary of portfolio health and limits."""
    try:
        account = get_account()
        positions = get_positions()

        equity = account['equity']
        total_exposure = account['portfolio_value'] - account['cash']
        exposure_pct = total_exposure / equity if equity > 0 else 0

        return {
            "equity": equity,
            "cash": account['cash'],
            "total_exposure_usd": total_exposure,
            "total_exposure_pct": exposure_pct,
            "is_within_limits": exposure_pct <= MAX_TOTAL_EXPOSURE_PCT,
            "num_positions": len(positions),
            "max_ticker_allowed_usd": equity * MAX_TICKER_EXPOSURE_PCT
        }
    except Exception as e:
        return {"error": str(e)}
