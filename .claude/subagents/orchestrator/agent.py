"""Orchestrator: Investment Desk with DETERMINISTIC workflow like Explorer Agent."""

import os
import sys
import logging
import argparse
import importlib.util
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from trading_mvp.core.db_manager import get_connection
from trading_mvp.core.dashboard_api_client import (
    save_desk_run, save_ticker_analysis, record_decision,
    get_active_watchlists
)
from trading_mvp.analysis.quant_stats import fetch_historical_stats
from trading_mvp.core.db_manager import get_news_for_ticker
from trading_mvp.core.dna_manager import DNAManager
from trading_mvp.core.portfolio_logic import get_portfolio_health
from trading_mvp.reporting.trade_cards import generate_trade_card

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_subagent(name: str, path: str):
    """Load a subagent module."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def get_portfolio_tickers() -> List[str]:
    """Get all tickers from current Alpaca portfolio positions."""
    tickers = set()
    try:
        from trading_mvp.execution.alpaca_orders import get_positions

        positions = get_positions()

        for pos in positions:
            symbol = pos.get('symbol')
            qty = float(pos.get('qty', 0))

            if qty > 0:  # Only positions with shares
                tickers.add(symbol)

        logger.info(f"📦 Loaded {len(tickers)} portfolio tickers from Alpaca")

    except Exception as e:
        logger.warning(f"Could not load portfolio tickers from Alpaca: {e}")

    return list(tickers)

def get_watchlist_tickers() -> List[str]:
    """Get all tickers from active watchlists."""
    tickers = set()
    try:
        watchlists = get_active_watchlists()
        for wl in watchlists:
            wl_id = wl['id']
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT ticker
                FROM watchlist_items
                WHERE watchlist_id = %s
            """, (wl_id,))

            tickers.update([row[0] for row in cursor.fetchall()])
            conn.close()

        logger.info(f"📋 Loaded {len(tickers)} watchlist tickers")

    except Exception as e:
        logger.warning(f"Could not load watchlist tickers: {e}")

    return list(tickers)

def get_all_relevant_tickers() -> List[str]:
    """Get all unique tickers from portfolio + watchlist."""
    portfolio_tickers = get_portfolio_tickers()
    watchlist_tickers = get_watchlist_tickers()

    all_tickers = list(set(portfolio_tickers + watchlist_tickers))
    logger.info(f"🎯 Total unique tickers to analyze: {len(all_tickers)}")

    return all_tickers

# =============================================================================
# MAIN WORKFLOW FUNCTIONS
# =============================================================================

def save_news_feed(ticker: str, news_items: List[Dict]) -> None:
    """Save processed news as a structured feed for a ticker.

    Args:
        ticker: Ticker symbol
        news_items: List of processed news dictionaries
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        for news in news_items:
            # Check if news already exists
            cursor.execute("SELECT id FROM news WHERE external_id = %s", (news.get('external_id', ''),))
            if cursor.fetchone():
                continue  # Skip duplicates

            # Insert news
            cursor.execute("""
                INSERT INTO news (title, summary, source, url, published_at, external_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                news.get('title', ''),
                news.get('summary', ''),
                news.get('source', ''),
                news.get('url', ''),
                news.get('published_at', ''),
                news.get('external_id', '')
            ))

            news_id = cursor.fetchone()[0]

            # Insert ticker-news mapping for feed
            cursor.execute("""
                INSERT INTO ticker_news_feed (ticker, news_id, processed_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (ticker, news_id) DO NOTHING
            """, (ticker, news_id, datetime.now().isoformat()))

        conn.commit()
        conn.close()
        logger.info(f"💾 Saved {len(news_items)} news items to feed for {ticker}")

    except Exception as e:
        logger.error(f"Error saving news feed for {ticker}: {e}")

def get_news_feed(ticker: str, limit: int = 10) -> str:
    """Get processed news feed for a ticker.

    Args:
        ticker: Ticker symbol
        limit: Max number of news items

    Returns:
        Formatted news feed string
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT n.title, n.summary, n.published_at
            FROM ticker_news_feed tnf
            JOIN news n ON tnf.news_id = n.id
            WHERE tnf.ticker = %s
            ORDER BY n.published_at DESC
            LIMIT %s
        """, (ticker, limit))

        news_items = cursor.fetchall()
        conn.close()

        if not news_items:
            return ""

        # Format feed
        feed_lines = []
        for title, summary, published_at in news_items:
            feed_lines.append(f"📰 {title}\n{summary}\n")

        return "\n".join(feed_lines)

    except Exception as e:
        logger.warning(f"Error getting news feed for {ticker}: {e}")
        return ""

def run_macro_analysis(tickers: List[str]) -> None:
    """STEP 1: Ingest and analyze news for all tickers."""
    logger.info("\n📰 STEP 1: MACRO & SENTIMENT ANALYSIS")

    try:
        macro_agent = load_subagent(
            "macro_analyst",
            os.path.join(os.path.dirname(__file__), "..", "macro_analyst", "agent.py")
        )

        # Check if we should skip news ingestion
        conn = get_connection()
        cursor = conn.cursor()
        four_hours_ago = datetime.now() - timedelta(hours=4)
        cursor.execute("SELECT COUNT(*) FROM news WHERE published_at > %s", (four_hours_ago.isoformat(),))
        recent_news_count = cursor.fetchone()[0]
        conn.close()

        if recent_news_count > 0:
            logger.info(f"✅ Found {recent_news_count} recent news items. Using existing data.")
        else:
            logger.info("📡 Ingesting fresh news...")
            macro_agent.ingest_and_analyze(tickers)

    except Exception as e:
        logger.error(f"Error in macro analysis: {e}")

def analyze_single_ticker(ticker: str, capital: float) -> Dict:
    """Analyze a SINGLE ticker with complete desk workflow.

    Returns:
        Complete analysis dict with bull/bear/risk/cio decisions
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"🔬 ANALYZING: {ticker}")
    logger.info(f"{'='*70}")

    # Load agents
    bull_agent = load_subagent(
        "bull_researcher",
        os.path.join(os.path.dirname(__file__), "..", "bull_researcher", "agent.py")
    )
    bear_agent = load_subagent(
        "bear_researcher",
        os.path.join(os.path.dirname(__file__), "..", "bear_researcher", "agent.py")
    )
    risk_agent = load_subagent(
        "risk_manager",
        os.path.join(os.path.dirname(__file__), "..", "risk_manager", "agent.py")
    )
    cio_agent = load_subagent(
        "cio",
        os.path.join(os.path.dirname(__file__), "..", "cio", "agent.py")
    )

    # Get context
    dna_manager = DNAManager()
    dna = dna_manager.get_dna(ticker)
    logger.info(f"🧬 DNA: {dna.get('asset_type', 'Unknown')}")

    # Try to get feed first (persistent)
    news_feed = get_news_feed(ticker, limit=10)
    news_context = ""

    if not news_feed:
        # If no feed, get from DB and save
        news_context = get_news_for_ticker(ticker, limit=10)

        # Save to feed
        if news_context:
            news_items = [{
                'title': 'Recent news',
                'summary': news_context,
                'source': 'aggregated',
                'published_at': datetime.now().isoformat(),
                'external_id': f"{ticker}_{datetime.now().strftime('%Y%m%d')}"
            }]
            save_news_feed(ticker, news_items)

        news_feed = news_context
    else:
        news_context = news_feed

    logger.info(f"📰 News feed: {len(news_feed)} chars")

    quant_stats = fetch_historical_stats(ticker)
    logger.info(f"📊 Quant: Trend={quant_stats.get('trend', 'N/A')}, RSI={quant_stats.get('rsi_14', 'N/A')}")

    # Bull & Bear Analysis
    logger.info("🐂 Running Bull analysis...")
    bull_case = bull_agent.analyze_bull_case(ticker, news_context=news_context, dna=dna)

    logger.info("🐻 Running Bear analysis...")
    bear_case = bear_agent.analyze_bear_case(ticker, news_context=news_context, dna=dna)

    # Risk Assessment
    logger.info("⚠️  Running Risk assessment...")
    risk_analysis = risk_agent.assess_risk(ticker, capital, dna=dna)

    # CIO Decision (INDIVIDUAL for this ticker)
    logger.info("🧠 Running CIO decision...")
    portfolio_state = get_portfolio_health()

    # Create single-ticker analysis for CIO
    single_ticker_analysis = [{
        "ticker": ticker,
        "sentiment_score": 0.0,  # Could calculate from news
        "quant_stats": quant_stats,
        "bull_case": bull_case,
        "bear_case": bear_case,
        "risk_analysis": risk_analysis,
        "requested_capital": capital,
    }]

    cio_decision = cio_agent.make_investment_decision(
        tickers_analysis=single_ticker_analysis,
        portfolio_state=portfolio_state,
        portfolio_metrics={},  # Could add
        strategy_metrics={},   # Could add
        macro_context=f"Individual analysis for {ticker}"
    )

    # Compile complete analysis
    complete_analysis = {
        "ticker": ticker,
        "dna": dna,
        "quant_stats": quant_stats,
        "news_context_length": len(news_context),
        "bull_case": bull_case,
        "bear_case": bear_case,
        "risk_analysis": risk_analysis,
        "cio_decision": cio_decision,
        "timestamp": datetime.now().isoformat()
    }

    # Also prepare ticker_result for database
    ticker_result = {
        'ticker': ticker,
        'company_name': dna.get('company_name', ticker),
        'recommendation': cio_decision.get('action', 'NONE'),
        'rationale': cio_decision.get('rationale', ''),
        'positive_ratio': bull_case.get('confidence', 0.7) if bull_case.get('overall_sentiment') == 'Strong Buy' else 0.5,
        'negative_ratio': bear_case.get('confidence', 0.3) if bear_case.get('overall_sentiment') == 'Strong Sell' else 0.2,
        'avg_confidence': 0.7,
        'related_news_count': len(news_context),
        'unique_entities_found': 0,
        'top_risks': risk_analysis.get('key_risks', []),
        'top_opportunities': bull_case.get('key_catalysts', []),
        'analysis_timestamp': datetime.now().isoformat()
    }

    # Log summary
    logger.info(f"\n📊 {ticker} SUMMARY:")
    logger.info(f"   🐂 Bull: {bull_case.get('overall_sentiment', 'N/A')}")
    logger.info(f"   🐻 Bear: {bear_case.get('overall_sentiment', 'N/A')}")
    logger.info(f"   ⚠️  Risk: {risk_analysis.get('risk_level', 'N/A')}")
    logger.info(f"   🧠 CIO: {cio_decision.get('action', 'N/A')} | Size: ${cio_decision.get('target_size_usd', 0):,.2f}")
    logger.info(f"   📝 Rationale: {cio_decision.get('rationale', 'N/A')[:100]}...")

    return complete_analysis, ticker_result

def execute_decision(ticker: str, decision: Dict, portfolio_state: Dict) -> Dict:
    """Execute trading decision for a single ticker."""
    action = decision.get('action', 'NONE')

    if action == 'NONE':
        return {"skipped": True, "reason": "No action required"}

    try:
        executioner = load_subagent(
            "executioner",
            os.path.join(os.path.dirname(__file__), "..", "executioner", "agent.py")
        )

        # Calculate quantity
        target_size = decision.get('target_size_usd', 1000)
        quantity = max(1, int(target_size / 100))  # Rough estimate

        logger.info(f"💼 Executing {action} {quantity} shares of {ticker}...")
        result = executioner.execute_trade(ticker, action, quantity)

        return result

    except Exception as e:
        logger.error(f"Error executing trade for {ticker}: {e}")
        return {"error": str(e)}

# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def run_investment_desk(capital: float = 1000.0, execute: bool = False) -> Dict:
    """Run COMPLETE investment desk workflow on ALL portfolio + watchlist assets.

    DETERMINISTIC WORKFLOW:
    1. Load ALL tickers from portfolio + watchlist
    2. Run macro/sentiment analysis for ALL
    3. For EACH ticker:
       - Bull analysis
       - Bear analysis
       - Risk assessment
       - CIO decision (individual)
    4. Execute ALL decisions (if execute=True)
    5. Persist EVERYTHING to database
    """

    # Check AUTOPILOT_MODE
    autopilot_mode = os.getenv("AUTOPILOT_MODE", "off").lower() == "on"
    if autopilot_mode:
        execute = True
        logger.info("🤖 AUTOPILOT MODE: ON")

    logger.info("\n" + "="*70)
    logger.info("🏛️  INVESTMENT DESK - DETERMINISTIC WORKFLOW")
    logger.info("="*70)
    logger.info(f"💰 Capital: ${capital:,.2f}")
    logger.info(f"🎯 Execute Trades: {execute}")

    # ========================================================================
    # STEP 0: LOAD ALL RELEVANT ASSETS
    # ========================================================================
    logger.info("\n📍 STEP 0: LOADING ASSETS")
    tickers = get_all_relevant_tickers()

    if not tickers:
        logger.error("❌ No tickers found in portfolio or watchlist!")
        return {"error": "No tickers to analyze"}

    # ========================================================================
    # STEP 1: MACRO & SENTIMENT (batch)
    # ========================================================================
    run_macro_analysis(tickers)

    # ========================================================================
    # STEP 2: CREATE DESK RUN
    # ========================================================================
    logger.info("\n💾 Creating desk run...")
    watchlists = get_active_watchlists()
    target_wl = watchlists[0]['id'] if watchlists else 1

    desk_run_id = save_desk_run(
        watchlist_id=target_wl,
        theme="Portfolio & Watchlist Analysis",
        tickers=tickers
    )
    logger.info(f"✅ Desk run ID: {desk_run_id}")

    # ========================================================================
    # STEP 3: ANALYZE EACH TICKER INDIVIDUALLY
    # ========================================================================
    logger.info(f"\n🔬 STEP 3: ANALYZING {len(tickers)} TICKERS")

    all_analyses = []
    execution_results = []

    for ticker in tickers:
        try:
            # Complete analysis for this ticker (returns both analysis and ticker_result)
            analysis, ticker_result = analyze_single_ticker(ticker, capital)
            all_analyses.append(analysis)

            # Save to database
            analysis_id = save_ticker_analysis(ticker_result, desk_run_id)
            logger.info(f"💾 Saved analysis ID: {analysis_id}")

            # Record CIO decision
            cio_decision = analysis['cio_decision']
            record_decision(
                ticker_analysis_id=analysis_id,
                desk_run_id=desk_run_id,
                ticker=ticker,
                recommendation=cio_decision.get('action', 'NONE'),
                desk_action=cio_decision.get('action', 'NONE'),
                decision="FOLLOWED" if execute else "WATCH",
                decision_notes=cio_decision.get('rationale', ''),
                action_taken="PENDING" if execute else "NONE",
                position_size=cio_decision.get('target_size_usd', 0)
            )

            # Execute if required
            if execute and cio_decision.get('action') in ['BUY', 'SELL']:
                exec_result = execute_decision(ticker, cio_decision, {})
                execution_results.append({
                    "ticker": ticker,
                    "result": exec_result
                })

        except Exception as e:
            logger.error(f"❌ Error analyzing {ticker}: {e}")
            all_analyses.append({
                "ticker": ticker,
                "error": str(e)
            })

    # ========================================================================
    # STEP 4: SUMMARY
    # ========================================================================
    logger.info("\n" + "="*70)
    logger.info("📊 INVESTMENT DESK SUMMARY")
    logger.info("="*70)

    buy_count = sum(1 for a in all_analyses if a.get('cio_decision', {}).get('action') == 'BUY')
    sell_count = sum(1 for a in all_analyses if a.get('cio_decision', {}).get('action') == 'SELL')
    hold_count = sum(1 for a in all_analyses if a.get('cio_decision', {}).get('action') in ['NONE', 'HOLD'])

    logger.info(f"📈 Total Analyzed: {len(all_analyses)}")
    logger.info(f"🟢 BUY Signals: {buy_count}")
    logger.info(f"🔴 SELL Signals: {sell_count}")
    logger.info(f"⚪ HOLD Signals: {hold_count}")

    if execution_results:
        logger.info(f"\n💼 EXECUTIONS:")
        for ex in execution_results:
            logger.info(f"   {ex['ticker']}: {ex['result']}")

    return {
        "desk_run_id": desk_run_id,
        "total_analyzed": len(all_analyses),
        "buy_signals": buy_count,
        "sell_signals": sell_count,
        "hold_signals": hold_count,
        "analyses": all_analyses,
        "executions": execution_results
    }

# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Investment Desk - Deterministic workflow for portfolio & watchlist analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze all portfolio + watchlist assets
  python agent.py --capital 5000

  # Analyze and execute trades
  python agent.py --execute --capital 10000

  # Enable AUTOPILOT MODE (automatic execution)
  AUTOPILOT_MODE=on python agent.py

Workflow:
  1. Load ALL tickers from portfolio + watchlist
  2. Run macro/sentiment analysis (batch)
  3. For EACH ticker:
     - Bull analysis
     - Bear analysis
     - Risk assessment
     - CIO decision (individual)
  4. Execute ALL decisions
  5. Persist EVERYTHING
        """
    )

    parser.add_argument("--capital", type=float, default=1000.0,
                       help="Capital per trade (default: $1000)")
    parser.add_argument("--execute", action="store_true",
                       help="Execute trades (default: False)")

    args = parser.parse_args()

    result = run_investment_desk(capital=args.capital, execute=args.execute)

    if "error" in result:
        logger.error(f"❌ {result['error']}")
        return 1

    logger.info("\n✅ Investment desk completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
