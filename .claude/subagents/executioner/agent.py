"""Executioner: Executes orders and manages positions in Alpaca."""

import os
import sys
import logging
import argparse
from typing import Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from trading_mvp.execution.alpaca_orders import submit_order, get_positions, get_account

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def execute_trade(symbol: str, action: str, qty: int, order_type: str = "market") -> Dict:
    """Execute a trade in Alpaca.

    Args:
        symbol: Ticker symbol
        action: 'BUY' or 'SELL'
        qty: Quantity
        order_type: 'market' or 'limit'

    Returns:
        Order confirmation
    """
    logger.info(f"Executing {action} order for {qty} shares of {symbol}")

    try:
        order = submit_order(
            symbol=symbol,
            qty=qty,
            side=action.lower(),
            order_type=order_type
        )

        logger.info(f"Order executed: {order['order_id']}")
        return order

    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        return {"error": str(e)}

def show_positions():
    """Show current positions."""
    try:
        positions = get_positions()
        account = get_account()

        print(f"\n{'='*80}")
        print(f"💼 CURRENT POSITIONS")
        print(f"{'='*80}")
        print(f"Portfolio Value: ${account.get('portfolio_value', 0):,.2f}")
        print(f"Buying Power: ${account.get('buying_power', 0):,.2f}\n")

        if positions:
            for pos in positions:
                pl_sign = "+" if pos.get('unrealized_pl', 0) >= 0 else ""
                print(f"{pos.get('symbol', 'N/A'):<6} {pos.get('qty', 0):>6} {pos.get('side', 'N/A'):<4} "
                      f"P&L: {pl_sign}{pos.get('unrealized_pl', 0):>10.2f}")
        else:
            print("No open positions")

        print(f"{'='*80}\n")
        return positions

    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        return []

def main():
    """Main entry point for Executioner CLI."""
    parser = argparse.ArgumentParser(description="Execute trades and manage positions")
    parser.add_argument("--symbol", type=str, help="Ticker symbol")
    parser.add_argument("--action", type=str, choices=['BUY', 'SELL'], help="BUY or SELL")
    parser.add_argument("--qty", type=int, help="Quantity")
    parser.add_argument("--type", type=str, default="market", choices=['market', 'limit'], help="Order type")
    parser.add_argument("--positions", action="store_true", help="Show current positions")

    args = parser.parse_args()

    if args.positions:
        show_positions()
    elif args.symbol and args.action and args.qty:
        execute_trade(args.symbol, args.action, args.qty, args.type)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
