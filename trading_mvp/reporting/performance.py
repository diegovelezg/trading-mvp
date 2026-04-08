"""Reportes de performance y análisis de cartera."""

from typing import Dict, List
from datetime import datetime, timedelta

def generate_performance_report(
    positions: List[Dict],
    account: Dict,
    period_days: int = 30
) -> str:
    """Generate a performance report for the portfolio.

    Args:
        positions: List of current positions
        account: Account information
        period_days: Period to analyze (default: 30 days)

    Returns:
        Formatted performance report as string
    """

    total_value = account.get('portfolio_value', 0)
    total_equity = account.get('equity', 0)
    cash = account.get('cash', 0)
    buying_power = account.get('buying_power', 0)

    # Calculate position statistics
    num_positions = len(positions)
    total_unrealized_pl = sum(pos.get('unrealized_pl', 0) for pos in positions)

    # Format positions list
    positions_text = ""
    if positions:
        for pos in positions[:10]:  # Limit to top 10
            symbol = pos.get('symbol', 'N/A')
            qty = pos.get('qty', 0)
            side = pos.get('side', 'N/A')
            pl = pos.get('unrealized_pl', 0)
            pl_pct = pos.get('unrealized_plpc', 0)

            pl_sign = "+" if pl >= 0 else ""
            positions_text += f"  {symbol:<6} {qty:>6} {side:<4} P&L: {pl_sign}{pl:>10.2f} ({pl_sign}{pl_pct:>6.2f}%)\n"
    else:
        positions_text = "  No open positions\n"

    report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PERFORMANCE REPORT - Last {period_days} Days                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

💼 PORTFOLIO SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Portfolio Value:    ${total_value:,.2f}
Equity:             ${total_equity:,.2f}
Cash:               ${cash:,.2f}
Buying Power:        ${buying_power:,.2f}
Open Positions:     {num_positions}

📊 CURRENT POSITIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{positions_text}💰 PERFORMANCE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Unrealized P&L: ${total_unrealized_pl:+,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Period: Last {period_days} days
╚══════════════════════════════════════════════════════════════════════════════╝
"""

    return report.strip()

def generate_daily_summary(
    trades_executed: List[Dict],
    news_processed: int,
    sentiment_changes: int
) -> str:
    """Generate a daily activity summary.

    Args:
        trades_executed: List of trades executed today
        news_processed: Number of news items processed
        sentiment_changes: Number of significant sentiment changes

    Returns:
        Formatted daily summary as string
    """

    trades_text = ""
    if trades_executed:
        for trade in trades_executed:
            symbol = trade.get('symbol', 'N/A')
            side = trade.get('side', 'N/A')
            qty = trade.get('qty', 0)
            price = trade.get('price', 0)
            trades_text += f"  {side:<4} {qty:>4} {symbol:<6} @ ${price:.2f}\n"
    else:
        trades_text = "  No trades executed today\n"

    summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          DAILY ACTIVITY SUMMARY                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📅 Date: {datetime.now().strftime('%Y-%m-%d')}

🤖 AGENT ACTIVITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
News Processed:      {news_processed}
Sentiment Changes:   {sentiment_changes}

💹 TRADES EXECUTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{trades_text}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
╚══════════════════════════════════════════════════════════════════════════════╝
"""

    return summary.strip()
