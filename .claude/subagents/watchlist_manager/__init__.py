"""Watchlist Manager Agent: Maintains watchlists and coordinates multi-agent analysis.

This agent is responsible for:
- Creating watchlists from Explorer Agent results
- Maintaining ticker watchlists with metadata
- Coordinating multi-agent analysis (GeoMacro, Sentiment, Risk)
- Generating watchlist status reports
"""

from .agent import (
    create_watchlist_from_explorer,
    analyze_watchlist,
    get_watchlist_status,
    list_watchlists
)

__all__ = [
    'create_watchlist_from_explorer',
    'analyze_watchlist',
    'get_watchlist_status',
    'list_watchlists'
]
