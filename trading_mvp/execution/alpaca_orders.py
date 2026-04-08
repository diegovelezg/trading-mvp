"""Ejecución de órdenes en Alpaca Paper Trading."""

import os
from typing import Dict, List, Optional
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv

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
