"""Watchlist Manager Agent: Maintains watchlists and coordinates multi-agent analysis."""

import os
import sys
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from trading_mvp.core.dashboard_api_client import (
    create_watchlist,
    add_ticker_to_watchlist,
    get_active_watchlists
)
from trading_mvp.utils.config_loader import get_default_watchlist_id

logger = logging.getLogger(__name__)


def create_watchlist_from_explorer(name: str, description: str, tickers: List[str],
                                  criteria_prompt: str, criteria_summary: str = None) -> Dict:
    """Create a watchlist from Explorer Agent results.

    Args:
        name: Watchlist name
        description: Description
        tickers: List of ticker symbols
        criteria_prompt: Original prompt
        criteria_summary: Structured summary

    Returns:
        Dict with watchlist_id and status
    """

    logger.info(f"📋 Creating watchlist '{name}' from Explorer Agent results...")

    # Create watchlist
    watchlist_id = create_watchlist(
        name=name,
        description=description,
        criteria_prompt=criteria_prompt,
        criteria_summary=criteria_summary
    )

    if not watchlist_id:
        logger.error(f"❌ Could not create watchlist")
        return {"success": False, "error": "Could not create watchlist"}

    # Add tickers (loop individual via Dashboard API)
    added_count = 0
    for ticker in tickers:
        if add_ticker_to_watchlist(
            watchlist_id=watchlist_id,
            ticker=ticker,
            reason=f"Discovered by Explorer Agent: {criteria_prompt}"
        ):
            added_count += 1

    logger.info(f"✅ Watchlist created: ID {watchlist_id} with {added_count} tickers")

    return {
        "success": True,
        "watchlist_id": watchlist_id,
        "ticker_count": added_count
    }


def analyze_watchlist(watchlist_id: int, hours_back: int = 48) -> Dict:
    """Analyze a watchlist using multiple agents.

    NOTA: Esta función está siendo deprecada.
    El análisis ahora se hace vía run_investment_desk.py que usa Dashboard APIs.

    Args:
        watchlist_id: Watchlist ID
        hours_back: Hours to look back for news

    Returns:
        Dict with analysis results
    """

    logger.warning("⚠️  analyze_watchlist() está deprecada. Usar run_investment_desk.py en su lugar.")

    # Get tickers from dashboard API
    watchlists = get_active_watchlists()
    watchlist = next((wl for wl in watchlists if wl['id'] == watchlist_id), None)

    if not watchlist:
        logger.error(f"❌ Watchlist {watchlist_id} not found")
        return {"success": False, "error": "Watchlist not found"}

    tickers = [item['ticker'] for item in watchlist.get('items', [])]

    logger.info(f"  📊 Analyzing {len(tickers)} tickers...")

    # Placeholder - análisis real se mueve a run_investment_desk.py
    return {
        "success": True,
        "watchlist_id": watchlist_id,
        "watchlist_name": watchlist['name'],
        "ticker_count": len(tickers),
        "results": []
    }


# Nota: get_news_for_ticker ELIMINADO - ya no usamos entity matching
# El sistema ahora usa semantic embeddings en su lugar


def get_watchlist_status(watchlist_id: int) -> Dict:
    """Get status of a watchlist via Dashboard API.

    Args:
        watchlist_id: Watchlist ID

    Returns:
        Dict with watchlist status
    """

    watchlists = get_active_watchlists()
    watchlist = next((wl for wl in watchlists if wl['id'] == watchlist_id), None)

    if not watchlist:
        return {"success": False, "error": "Watchlist not found"}

    return {
        "success": True,
        "watchlist": watchlist,
        "tickers": watchlist.get('items', []),
        "ticker_count": watchlist.get('ticker_count', 0)
    }


def list_watchlists() -> List[Dict]:
    """List all active watchlists via Dashboard API.

    Returns:
        List of watchlist dicts (ya incluye items y ticker_count)
    """

    return get_active_watchlists()


# Main function for agent execution
if __name__ == "__main__":
    import json

    # Example: Create watchlist from Explorer Agent (via Dashboard API)
    result = create_watchlist_from_explorer(
        name="Renewable Energy Small Caps",
        description="High growth renewable energy companies under $5B market cap",
        tickers=["SEDG", "ENPH", "RUN", "FSLR", "NOVA"],
        criteria_prompt="Renewable Energy small caps with strong balance sheets",
        criteria_summary="Small cap renewable energy companies with strong fundamentals"
    )

    print(json.dumps(result, indent=2))
