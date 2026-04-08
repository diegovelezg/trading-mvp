"""Explorer Agent: Thematic research scout for discovering stock tickers.

This subagent uses Gemini AI to identify clusters of stock tickers based on
high-level thematic prompts like "AI infrastructure" or "Renewable energy small caps".
"""

from .agent import discover_tickers, handover_to_analyst, main

__all__ = ["discover_tickers", "handover_to_analyst", "main"]
