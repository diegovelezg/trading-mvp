"""Ejecución de órdenes en Alpaca Paper Trading."""

import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import date
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

def get_trading_client() -> TradingClient:
    """Get authenticated Alpaca trading client."""
    api_key = os.getenv("ALPACA_PAPER_API_KEY")
    secret_key = os.getenv("PAPER_API_SECRET")

    if not api_key or not secret_key:
        raise ValueError("ALPACA_PAPER_API_KEY and PAPER_API_SECRET required (same keys as news API)")

    return TradingClient(
        api_key=api_key,
        secret_key=secret_key,
        paper=True  # Use paper trading
    )

def check_execution_guardrails() -> Tuple[bool, str]:
    """Check if we can still trade today based on human-defined limits.
    
    Returns:
        (is_allowed, reason)
    """
    try:
        client = get_trading_client()
        account = client.get_account()
        
        # 1. Check Daily Drawdown Limit
        # last_equity is the equity at the close of the previous trading day
        equity = float(account.equity)
        last_equity = float(account.last_equity)
        
        drawdown = (equity - last_equity) / last_equity if last_equity > 0 else 0
        limit_drawdown = float(os.getenv("DAILY_DRAWDOWN_LIMIT_PCT", "0.03"))
        
        if drawdown < -limit_drawdown:
            return False, f"Daily drawdown limit reached: {drawdown:.2%} (Limit: {limit_drawdown:.2%})"
            
        # 2. Check Max Trades Per Day
        # Get orders from today
        today = date.today().isoformat()

        # Note: We use GetOrdersRequest to filter by date
        # In Alpaca SDK, we might need to handle pagination if there are many orders
        # Get all orders (no status filter) to count today's activity
        orders = client.get_orders(GetOrdersRequest(after=today))
        
        # Count filled or open buy/sell orders (excluding cancellations)
        active_statuses = [OrderStatus.FILLED, OrderStatus.PARTIALLY_FILLED, OrderStatus.NEW, OrderStatus.ACCEPTED]
        trade_count = len([o for o in orders if o.status in active_statuses])
        
        limit_trades = int(os.getenv("MAX_TRADES_PER_DAY", "10"))
        if trade_count >= limit_trades:
            return False, f"Maximum daily trades reached: {trade_count} (Limit: {limit_trades})"
            
        return True, "All guardrails passed"
        
    except Exception as e:
        logger.error(f"Error checking guardrails: {e}")
        # If we can't check, we fail safe (stop trading)
        return False, f"Guardrail check failed: {str(e)}"

def submit_order(
    symbol: str,
    qty: int,
    side: str,
    order_type: str = "market",
    limit_price: Optional[float] = None,
    time_in_force: str = "day"
) -> Dict:
    """Submit an order to Alpaca.

    Args:
        symbol: Ticker symbol
        qty: Quantity of shares
        side: 'buy' or 'sell'
        order_type: 'market' or 'limit'
        limit_price: Limit price (required for limit orders)
        time_in_force: 'day', 'gtc', etc.

    Returns:
        Order confirmation dict
    """
    # FINAL SAFETY CHECK
    is_allowed, reason = check_execution_guardrails()
    if not is_allowed:
        logger.error(f"🚫 EXECUTION BLOCKED: {reason}")
        raise PermissionError(f"Trade rejected by Risk Guardrails: {reason}")

    client = get_trading_client()

    side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL

    if order_type.lower() == 'market':
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY
        )
    else:
        if not limit_price:
            raise ValueError("limit_price required for limit orders")
        order_data = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            limit_price=limit_price,
            time_in_force=TimeInForce.DAY
        )

    order = client.submit_order(order_data)

    return {
        "order_id": order.id,
        "symbol": order.symbol,
        "qty": order.qty,
        "side": order.side,
        "type": order.type,
        "status": order.status
    }

def get_open_orders() -> List[Dict]:
    """Get all open/pending orders from Alpaca."""
    client = get_trading_client()
    # Get only open orders
    from alpaca.trading.requests import GetOrdersRequest
    orders = client.get_orders(GetOrdersRequest(status="open"))

    return [
        {
            "order_id": order.id,
            "symbol": order.symbol,
            "qty": order.qty,
            "side": order.side,
            "type": order.type,
            "status": order.status,
            "limit_price": order.limit_price,
            "created_at": order.created_at.isoformat() if order.created_at else None
        }
        for order in orders
    ]

def get_positions() -> List[Dict]:
    """Get current positions from Alpaca."""
    client = get_trading_client()
    positions = client.get_all_positions()

    return [
        {
            "symbol": pos.symbol,
            "qty": pos.qty,
            "side": pos.side,
            "avg_entry_price": pos.avg_entry_price,
            "current_price": pos.current_price,
            "unrealized_pl": pos.unrealized_pl,
            "unrealized_plpc": pos.unrealized_plpc
        }
        for pos in positions
    ]

def get_account() -> Dict:
    """Get account information from Alpaca."""
    client = get_trading_client()
    account = client.get_account()

    return {
        "buying_power": float(account.buying_power),
        "cash": float(account.cash),
        "portfolio_value": float(account.portfolio_value),
        "equity": float(account.equity)
    }
