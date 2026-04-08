"""Generación de Trade Cards para decisiones de inversión."""

from typing import Dict, List
from datetime import datetime

def generate_trade_card(
    symbol: str,
    action: str,
    hypothesis: Dict,
    bull_case: Dict,
    bear_case: Dict,
    risk_analysis: Dict,
    sentiment_score: float
) -> str:
    """Generate a formatted trade card for an investment decision.

    Args:
        symbol: Ticker symbol
        action: 'BUY', 'SELL', or 'HOLD'
        hypothesis: Investment hypothesis from Hypothesis Generator
        bull_case: Bullish arguments from Bull Researcher
        bear_case: Bearish arguments from Bear Researcher
        risk_analysis: Risk assessment from Risk Manager
        sentiment_score: Sentiment score from Macro Analyst

    Returns:
        Formatted trade card as string
    """

    card = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          TRADE CARD - {symbol:<20}                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│ RECOMMENDATION: {action:<68} │
└──────────────────────────────────────────────────────────────────────────────┘

📊 INVESTMENT HYPOTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{hypothesis.get('thesis', 'N/A')}

🎯 KEY DRIVERS
{format_drivers(hypothesis.get('drivers', []))}

📈 BULL CASE (Positives)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{format_arguments(bull_case.get('arguments', []))}

⚠️ BEAR CASE (Risks)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{format_arguments(bear_case.get('arguments', []))}

⚡ RISK ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Position Size:    {risk_analysis.get('position_size', 'N/A')}
Stop Loss:       {risk_analysis.get('stop_loss', 'N/A')}
Take Profit:     {risk_analysis.get('take_profit', 'N/A')}
Risk/Reward:     {risk_analysis.get('risk_reward', 'N/A')}
Max Drawdown:    {risk_analysis.get('max_drawdown', 'N/A')}

💰 SENTIMENT SCORE: {sentiment_score:+.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
╚══════════════════════════════════════════════════════════════════════════════╝
"""

    return card.strip()

def format_drivers(drivers: List[str]) -> str:
    """Format key drivers list."""
    if not drivers:
        return "No drivers specified"

    return "\n".join([f"• {driver}" for driver in drivers])

def format_arguments(arguments: List[str]) -> str:
    """Format arguments list."""
    if not arguments:
        return "No arguments provided"

    return "\n".join([f"• {arg}" for arg in arguments])
