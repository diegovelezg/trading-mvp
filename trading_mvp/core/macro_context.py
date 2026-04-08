"""Macro Context Utility - Interface for agents to query GeoMacro insights."""

import logging
from typing import List, Dict, Optional
from trading_mvp.core.db_geo_macro import (
    get_recent_insights,
    get_insights_for_ticker,
    get_insights_for_sector,
    get_insights_for_region,
    get_critical_insights
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_macro_context_for_analysis(
    ticker: Optional[str] = None,
    sector: Optional[str] = None,
    region: Optional[str] = None,
    hours: int = 48,
    min_importance: str = "medium"
) -> Dict:
    """Get relevant macro context for investment analysis.

    This is the MAIN function that other agents should use to get macro context.

    Args:
        ticker: Specific ticker symbol (optional)
        sector: Sector context (optional)
        region: Geographic focus (optional)
        hours: Hours to look back (default: 48)
        min_importance: Minimum importance level (default: medium)

    Returns:
        Dictionary with macro context information
    """
    logger.info(f"🌍 Fetching macro context for: ticker={ticker}, sector={sector}, region={region}")

    context = {
        "ticker": ticker,
        "sector": sector,
        "region": region,
        "timeframe_hours": hours,
        "insights": [],
        "critical_alerts": [],
        "summary": ""
    }

    # Get critical insights first (always included)
    critical = get_critical_insights(hours=hours)
    context["critical_alerts"] = critical

    # Get specific insights based on parameters
    if ticker:
        ticker_insights = get_insights_for_ticker(ticker, hours=hours)
        context["insights"].extend(ticker_insights)

    if sector:
        sector_insights = get_insights_for_sector(sector, hours=hours)
        context["insights"].extend(sector_insights)

    if region:
        region_insights = get_insights_for_region(region, hours=hours)
        context["insights"].extend(region_insights)

    # If no specific filters, get all recent insights
    if not any([ticker, sector, region]):
        recent_insights = get_recent_insights(hours=hours, min_importance=min_importance)
        context["insights"].extend(recent_insights)

    # Remove duplicates (based on insight ID)
    seen_ids = set()
    unique_insights = []
    for insight in context["insights"]:
        if insight['id'] not in seen_ids:
            seen_ids.add(insight['id'])
            unique_insights.append(insight)

    context["insights"] = unique_insights

    # Generate summary
    context["summary"] = _generate_context_summary(context)

    logger.info(f"✅ Found {len(context['insights'])} insights, {len(context['critical_alerts'])} critical alerts")

    return context

def _generate_context_summary(context: Dict) -> str:
    """Generate a human-readable summary of macro context.

    Args:
        context: Context dictionary

    Returns:
        Formatted summary string
    """
    summary_parts = []

    # Critical alerts
    if context["critical_alerts"]:
        summary_parts.append(f"🚨 {len(context['critical_alerts'])} CRITICAL alerts:")
        for alert in context["critical_alerts"][:3]:  # Top 3
            summary_parts.append(f"  • {alert['title']}")

    # Regular insights
    if context["insights"]:
        importance_counts = {}
        for insight in context["insights"]:
            imp = insight["importance"]
            importance_counts[imp] = importance_counts.get(imp, 0) + 1

        summary_parts.append(f"\n📊 {len(context['insights'])} relevant insights:")
        for imp, count in sorted(importance_counts.items(), key=lambda x: x[1], reverse=True):
            summary_parts.append(f"  • {count} {imp.upper()}")

    return "\n".join(summary_parts) if summary_parts else "No significant macro events detected."

def format_macro_context_for_prompt(context: Dict) -> str:
    """Format macro context for inclusion in AI prompts.

    This formats the macro context in a way that can be easily included
    in prompts for other agents (Explorer, Hypothesis Generator, etc.)

    Args:
        context: Macro context dictionary

    Returns:
        Formatted string for prompt inclusion
    """
    if not context["insights"] and not context["critical_alerts"]:
        return "No significant macro events detected in the specified timeframe."

    prompt_parts = []

    # Header
    prompt_parts.append("## RELEVANT MACRO CONTEXT ##\n")

    # Critical alerts first
    if context["critical_alerts"]:
        prompt_parts.append("CRITICAL ALERTS:")
        for alert in context["critical_alerts"]:
            prompt_parts.append(f"- [{alert['event_type'].upper()}] {alert['title']}")
            prompt_parts.append(f"  Impact: {alert['impact_analysis'][:200]}...")
            prompt_parts.append("")

    # Regular insights
    if context["insights"]:
        prompt_parts.append("RELEVANT INSIGHTS:")
        for insight in context["insights"][:10]:  # Limit to 10 most relevant
            prompt_parts.append(f"- [{insight['importance'].upper()}] {insight['title']}")
            prompt_parts.append(f"  {insight['summary']}")
            prompt_parts.append("")

    return "\n".join(prompt_parts)

# Convenience functions for specific use cases

def get_macro_context_for_explorer(theme: str, hours: int = 48) -> str:
    """Get macro context formatted for Explorer Agent.

    Args:
        theme: Investment theme being explored
        hours: Hours to look back

    Returns:
        Formatted macro context string
    """
    context = get_macro_context_for_analysis(hours=hours)
    return format_macro_context_for_prompt(context)

def get_macro_context_for_hypothesis(tickers: List[str], hours: int = 72) -> str:
    """Get macro context formatted for Hypothesis Generator.

    Args:
        tickers: List of tickers being analyzed
        hours: Hours to look back

    Returns:
        Formatted macro context string
    """
    all_insights = []
    for ticker in tickers:
        context = get_macro_context_for_analysis(ticker=ticker, hours=hours)
        all_insights.extend(context["insights"])

    # Create combined context
    combined_context = {
        "insights": all_insights,
        "critical_alerts": []
    }

    # Add critical alerts
    critical = get_critical_insights(hours=hours)
    combined_context["critical_alerts"] = critical

    return format_macro_context_for_prompt(combined_context)

def get_macro_context_for_risk(ticker: str, hours: int = 72) -> Dict:
    """Get detailed macro context for Risk Manager.

    Args:
        ticker: Ticker being risk-assessed
        hours: Hours to look back

    Returns:
        Full macro context dictionary (not formatted)
    """
    return get_macro_context_for_analysis(
        ticker=ticker,
        hours=hours,
        min_importance="low"  # Get all insights for risk assessment
    )

def check_for_critical_events(hours: int = 24) -> bool:
    """Quick check if there are any critical macro events.

    Args:
        hours: Hours to look back

    Returns:
        True if critical events exist, False otherwise
    """
    critical = get_critical_insights(hours=hours)
    return len(critical) > 0
