"""Watchlist Manager Agent: Maintains watchlists and coordinates multi-agent analysis."""

import os
import sys
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from trading_mvp.core.db_watchlist import (
    create_watchlist_tables,
    create_watchlist,
    add_tickers_batch_to_watchlist,
    get_watchlist,
    get_watchlist_tickers,
    get_active_watchlists,
    save_watchlist_analysis,
    get_watchlist_analysis
)

logger = logging.getLogger(__name__)

# Ticker to Entity mapping (static for now, can be made dynamic)
TICKER_TO_ENTITIES = {
    # Energy/Oil
    "USO": ["Crude Oil", "Oil", "Energy", "Commodities", "WTI"],
    "XLE": ["Energy", "Oil & Gas", "SPDR", "ETF", "Sector"],
    "XOP": ["Energy", "Oil & Gas", "Exploration", "ETF"],
    "BNO": ["Brent Oil", "Oil", "Energy", "Commodities"],
    "COP": ["Oil & Gas", "Energy", "Crude Oil", "Exploration & Production", "Commodities"],
    "CVE": ["Oil & Gas", "Energy", "Canadian Oil", "Tar Sands", "Integrated Oil"],

    # Technology
    "AAPL": ["Technology", "Consumer", "Hardware", "Semiconductors", "Mobile"],
    "MSFT": ["Technology", "Software", "Cloud", "Enterprise"],
    "GOOGL": ["Technology", "Internet", "Search", "Advertising", "Cloud"],
    "META": ["Technology", "Social Media", "Internet", "Advertising"],
    "NVDA": ["Technology", "Semiconductors", "AI", "Hardware", "Chips"],
    "AMD": ["Technology", "Semiconductors", "Hardware", "Chips"],

    # Renewable Energy
    "ENPH": ["Solar Energy", "Renewable Energy", "Technology", "Residential"],
    "SEDG": ["Solar Energy", "Renewable Energy", "Technology", "Commercial"],
    "FSLR": ["Solar Energy", "Renewable Energy", "Technology"],
    "RUN": ["Solar Energy", "Renewable Energy", "Technology", "Residential"],
    "CSIQ": ["Solar Energy", "Renewable Energy", "Technology"],
    "PLUG": ["Clean Energy", "Battery Technology", "Renewable Energy"],
    "BE": ["Electric Vehicle", "Battery Technology", "Clean Energy"],

    # Finance
    "JPM": ["Finance", "Banking", "Financial Services"],
    "BAC": ["Finance", "Banking", "Financial Services"],
    "WFC": ["Finance", "Banking", "Financial Services"],
    "C": ["Finance", "Banking", "Financial Services"],
    "GS": ["Finance", "Investment Banking", "Financial Services"],
    "MA": ["Mastercard", "Payments", "Finance", "Credit Cards"],

    # Nuclear & Uranium
    "NXE": ["NexGen Energy", "Uranium", "Nuclear Energy", "Saskatchewan"],
    "CCJ": ["Cameco", "Uranium", "Nuclear Energy", "Fuel Cycle"],
    "URA": ["Uranium ETF", "Uranium", "Nuclear Power", "Clean Energy"],
    "BWXT": ["BWX Technologies", "Nuclear Reactors", "SMR", "Naval Nuclear"],
    "SMR": ["NuScale Power", "Small Modular Reactors", "Nuclear Technology"],
    "UUUU": ["Energy Fuels", "Uranium", "Rare Earth Elements"],
    "DNN": ["Denison Mines", "Uranium", "Athabasca Basin"]
}


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

    # Add tickers
    ticker_items = [
        {"ticker": t, "reason": f"Discovered by Explorer Agent: {criteria_prompt}"}
        for t in tickers
    ]

    added_count = add_tickers_batch_to_watchlist(watchlist_id, ticker_items)

    logger.info(f"✅ Watchlist created: ID {watchlist_id} with {added_count} tickers")

    return {
        "success": True,
        "watchlist_id": watchlist_id,
        "ticker_count": added_count
    }


def analyze_watchlist(watchlist_id: int, hours_back: int = 48) -> Dict:
    """Analyze a watchlist using multiple agents.

    Args:
        watchlist_id: Watchlist ID
        hours_back: Hours to look back for news

    Returns:
        Dict with analysis results
    """

    logger.info(f"🔍 Analyzing watchlist {watchlist_id}...")

    # Get watchlist details
    watchlist = get_watchlist(watchlist_id)
    if not watchlist:
        logger.error(f"❌ Watchlist {watchlist_id} not found")
        return {"success": False, "error": "Watchlist not found"}

    # Get tickers
    tickers_data = get_watchlist_tickers(watchlist_id)
    tickers = [t['ticker'] for t in tickers_data]

    logger.info(f"  📊 Analyzing {len(tickers)} tickers...")

    results = []
    data_sources = []

    for ticker in tickers:
        logger.info(f"    🎯 Analyzing {ticker}...")

        # For now, just store placeholder analysis
        # In the future, this will call:
        # - GeoMacro Analyst: get_news_for_ticker(ticker)
        # - Sentiment Analyst: analyze_sentiment(ticker)
        # - Risk Manager: assess_risk(ticker)

        geomacro_score = 0.0  # Placeholder
        sentiment_score = 0.0  # Placeholder
        risk_score = 0.5  # Placeholder

        # Save analysis
        save_watchlist_analysis(
            watchlist_id=watchlist_id,
            ticker=ticker,
            geomacro_score=geomacro_score,
            sentiment_score=sentiment_score,
            risk_score=risk_score,
            data_sources=["placeholder"]  # Will be real agents
        )

        results.append({
            "ticker": ticker,
            "geomacro_score": geomacro_score,
            "sentiment_score": sentiment_score,
            "risk_score": risk_score
        })

    logger.info(f"✅ Analysis complete for {len(results)} tickers")

    return {
        "success": True,
        "watchlist_id": watchlist_id,
        "watchlist_name": watchlist['name'],
        "ticker_count": len(results),
        "results": results
    }


def get_ticker_entities(ticker: str) -> List[str]:
    """Get entities for a ticker.

    Args:
        ticker: Ticker symbol

    Returns:
        List of entity names
    """

    ticker = ticker.upper()
    return TICKER_TO_ENTITIES.get(ticker, [])


def get_news_for_ticker(ticker: str, hours_back: int = 24) -> List[Dict]:
    """Get news for a ticker via entity matching.

    Args:
        ticker: Ticker symbol
        hours_back: Hours to look back

    Returns:
        List of news items
    """

    # Get ticker's entities
    ticker_entities = get_ticker_entities(ticker)

    if not ticker_entities:
        logger.warning(f"⚠️  No entities found for {ticker}")
        return []

    # Query news with those entities
    from trading_mvp.core.db_geo_news import get_recent_news

    all_news = get_recent_news(hours_back=hours_back, limit=100)

    # Filter news that mention ticker's entities
    relevant_news = []
    for news in all_news:
        if not news:
            continue

        title = news.get('title', '') or ''
        summary = news.get('summary', '') or ''

        title_lower = title.lower() if isinstance(title, str) else ''
        summary_lower = summary.lower() if isinstance(summary, str) else ''

        # Check if any entity is mentioned
        for entity in ticker_entities:
            if entity.lower() in title_lower or entity.lower() in summary_lower:
                relevant_news.append(news)
                break

    logger.info(f"📰 Found {len(relevant_news)} news items for {ticker} via entities")
    return relevant_news


def get_watchlist_status(watchlist_id: int) -> Dict:
    """Get status of a watchlist.

    Args:
        watchlist_id: Watchlist ID

    Returns:
        Dict with watchlist status
    """

    watchlist = get_watchlist(watchlist_id)
    if not watchlist:
        return {"success": False, "error": "Watchlist not found"}

    tickers = get_watchlist_tickers(watchlist_id)
    analysis = get_watchlist_analysis(watchlist_id, hours_back=48)

    return {
        "success": True,
        "watchlist": {
            "id": watchlist['id'],
            "name": watchlist['name'],
            "description": watchlist['description'],
            "criteria_prompt": watchlist['criteria_prompt'],
            "criteria_summary": watchlist['criteria_summary'],
            "status": watchlist['status'],
            "created_at": watchlist['created_at']
        },
        "tickers": tickers,
        "recent_analysis": analysis
    }


def list_watchlists() -> List[Dict]:
    """List all active watchlists.

    Returns:
        List of watchlist dicts
    """

    watchlists = get_active_watchlists()

    # Add ticker counts
    for wl in watchlists:
        wl_id = wl['id']
        tickers = get_watchlist_tickers(wl_id)
        wl['ticker_count'] = len(tickers)

    return watchlists


# Main function for agent execution
if __name__ == "__main__":
    import json

    # Initialize database
    create_watchlist_tables()

    # Example: Create watchlist from Explorer Agent
    result = create_watchlist_from_explorer(
        name="Renewable Energy Small Caps",
        description="High growth renewable energy companies under $5B market cap",
        tickers=["SEDG", "ENPH", "RUN", "FSLR", "NOVA"],
        criteria_prompt="Renewable Energy small caps with strong balance sheets",
        criteria_summary="Small cap renewable energy companies with strong fundamentals"
    )

    print(json.dumps(result, indent=2))
