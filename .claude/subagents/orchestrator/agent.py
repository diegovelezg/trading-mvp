"""Orchestrator: Coordinates all subagents for complete investment workflow using real agents."""

import os
import sys
import logging
import argparse
from typing import List, Dict
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()  # CRITICAL: Load .env for AUTOPILOT_MODE

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from trading_mvp.reporting.trade_cards import generate_trade_card
from trading_mvp.core.db_manager import get_connection

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def should_skip_news_ingestion() -> bool:
    """Check if there are recent news items (< 4 hours old).

    Returns:
        True if news ingestion should be skipped, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check for news items in the last 4 hours
        four_hours_ago = datetime.now() - timedelta(hours=4)
        cursor.execute("""
            SELECT COUNT(*)
            FROM news
            WHERE published_at > ?
        """, (four_hours_ago.isoformat(),))

        count = cursor.fetchone()[0]
        conn.close()

        if count > 0:
            logger.info(f"✅ Found {count} recent news items (< 4 hours old). Skipping news ingestion.")
            return True

        return False

    except Exception as e:
        logger.warning(f"Error checking recent news: {e}. Proceeding with ingestion.")
        return False

def get_avg_sentiment(ticker: str) -> float:
    """Get average sentiment score for a ticker from database.

    Args:
        ticker: Ticker symbol

    Returns:
        Average sentiment score (-1 to 1), or 0 if no data
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get average sentiment for this ticker
        cursor.execute("""
            SELECT AVG(s.score)
            FROM sentiments s
            JOIN news n ON s.news_id = n.id
            WHERE n.title LIKE ? OR n.summary LIKE ?
        """, (f"%{ticker}%", f"%{ticker}%"))

        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            return float(result[0])
        return 0.0

    except Exception as e:
        logger.warning(f"Could not get sentiment for {ticker}: {e}")
        return 0.0

def orchestrate_investment_workflow(theme: str, capital: float = 1000.0, execute: bool = False) -> Dict:
    """Orchestrate complete investment workflow from discovery to execution using CIO and Portfolio Logic."""

    # Check AUTOPILOT_MODE
    autopilot_mode = os.getenv("AUTOPILOT_MODE", "off").lower() == "on"
    if autopilot_mode:
        execute = True  # Force execution when autopilot is ON
        logger.info("🤖 AUTOPILOT MODE: ON - Automatic execution enabled")

    logger.info(f"🚀 Starting EVOLVED investment workflow for theme: {theme}")
    logger.info(f"💰 Initial Capital Request: ${capital:,.2f}")
    logger.info(f"🎯 Execute Trades: {execute}")

    try:
        subagents_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        import importlib.util

        # ========================================================================
        # STEP 1: DISCOVERY (Explorer Agent)
        # ========================================================================
        logger.info("\n📍 STEP 1: DISCOVERY")
        explorer_path = os.path.join(subagents_dir, "explorer", "agent.py")
        spec = importlib.util.spec_from_file_location("explorer", explorer_path)
        explorer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(explorer_module)

        discovery_results = explorer_module.discover_tickers(theme)
        if not discovery_results:
            return {"error": "No tickers discovered"}

        # Extract symbols for the analysis flow
        tickers = [r['ticker'] for r in discovery_results[:3]] # Limit to 3 for deep analysis
        logger.info(f"✅ Discovered candidates: {tickers}")

        # AUTO-POPULATE WATCHLIST WITH SPANISH DESCRIPTIONS
        try:
            from trading_mvp.core.dashboard_api_client import add_ticker_to_watchlist, get_active_watchlists
            watchlists = get_active_watchlists()
            if watchlists:
                target_wl = watchlists[0]['id'] # Use the first active watchlist
                for res in discovery_results:
                    add_ticker_to_watchlist(
                        watchlist_id=target_wl,
                        ticker=res['ticker'],
                        company_name=res['name'],
                        reason=res['description_es']
                    )
                logger.info(f"📋 Watchlist updated with {len(discovery_results)} tickers in Spanish.")
        except Exception as e:
            logger.warning(f"⚠️ Could not auto-populate watchlist: {e}")

        # ========================================================================
        # STEP 2: MACRO & SENTIMENT (Macro Analyst)
        # ========================================================================
        logger.info(f"\n📰 STEP 2: MACRO & SENTIMENT")

        # Check if we should skip news ingestion
        skip_news = should_skip_news_ingestion()

        macro_path = os.path.join(subagents_dir, "macro_analyst", "agent.py")
        spec = importlib.util.spec_from_file_location("macro_analyst", macro_path)
        macro_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(macro_module)

        if not skip_news:
            macro_module.ingest_and_analyze(tickers)
        else:
            logger.info("⏭️  Skipping news ingestion - using existing data")
        
        # ========================================================================
        # STEP 3: MESA ANALYSIS (Batch Bull, Bear, Risk)
        # ========================================================================
        logger.info(f"\n⚖️  STEP 3: MESA ANALYSIS (Batch)")
        
        # Load agents
        bull_path = os.path.join(subagents_dir, "bull_researcher", "agent.py")
        bear_path = os.path.join(subagents_dir, "bear_researcher", "agent.py")
        risk_path = os.path.join(subagents_dir, "risk_manager", "agent.py")
        
        def load_mod(name, path):
            s = importlib.util.spec_from_file_location(name, path)
            m = importlib.util.module_from_spec(s)
            s.loader.exec_module(m)
            return m

        bull_mod = load_mod("bull", bull_path)
        bear_mod = load_mod("bear", bear_path)
        risk_mod = load_mod("risk", risk_path)

        desk_results = []
        from trading_mvp.analysis.quant_stats import fetch_historical_stats

        for ticker in tickers:
            logger.info(f"--- Deep Analyzing {ticker} ---")
            
            # Quantitative Analysis Snapshot
            quant_stats = fetch_historical_stats(ticker)
            logger.info(f"📊 Quant Snapshot: Trend={quant_stats.get('trend')}, RSI={quant_stats.get('rsi_14')}")

            sentiment = get_avg_sentiment(ticker)
            bull_case = bull_mod.analyze_bull_case(ticker)
            bear_case = bear_mod.analyze_bear_case(ticker)
            
            # Risk Manager now has deeper context
            risk_analysis = risk_mod.assess_risk(ticker, capital)
            
            # CAPTURE EVERYTHING (The whole report)
            full_ticker_report = {
                "ticker": ticker,
                "sentiment_score": sentiment,
                "quant_stats": quant_stats,
                "bull_case": bull_case,
                "bear_case": bear_case,
                "risk_analysis": risk_analysis,
                "requested_capital": capital,
                "recommendation": bull_case.get('overall_sentiment', 'NEUTRAL'),
                "rationale": bull_case.get('deep_analysis', 'N/A')
            }
            
            desk_results.append(full_ticker_report)

        # ========================================================================
        # STEP 4: CIO DECISION (The Brain)
        # ========================================================================
        logger.info(f"\n🧠 STEP 4: CIO DECISION")
        cio_path = os.path.join(subagents_dir, "cio", "agent.py")
        cio_mod = load_mod("cio", cio_path)
        
        from trading_mvp.core.portfolio_logic import get_portfolio_health
        from trading_mvp.analysis.portfolio_stats import calculate_portfolio_metrics
        from trading_mvp.analysis.strategy_stats import calculate_strategy_stats
        from trading_mvp.core.dashboard_api_client import save_ticker_analysis, record_decision, save_desk_run

        portfolio_state = get_portfolio_health()
        portfolio_metrics = calculate_portfolio_metrics()
        strategy_metrics = calculate_strategy_stats()
        
        logger.info(f"📈 STRATEGY SELF-AWARENESS: Sharpe={portfolio_metrics.get('sharpe_ratio')}, Win Rate={strategy_metrics.get('win_rate')}%")

        cio_decision = cio_mod.make_investment_decision(
            tickers_analysis=desk_results,
            portfolio_state=portfolio_state,
            portfolio_metrics=portfolio_metrics,
            strategy_metrics=strategy_metrics,
            macro_context=f"Theme: {theme}"
        )
        
        # PERSIST TO DATABASE FOR OBSERVABILITY
        try:
            # 1. Create a real desk run record
            from trading_mvp.core.dashboard_api_client import get_active_watchlists
            watchlists = get_active_watchlists()
            target_wl = watchlists[0]['id'] if watchlists else 1
            
            desk_run_id = save_desk_run(
                watchlist_id=target_wl,
                theme=theme,
                overall_sentiment=cio_decision.get('conviction_score', 5) / 10.0 # Scale to 0-1
            )
            
            for res in desk_results:
                t_analysis_id = save_ticker_analysis(res, desk_run_id)
                
                # If this ticker was the winner chosen by the CIO
                if res['ticker'] == cio_decision.get('selected_ticker'):
                    record_decision(
                        ticker_analysis_id=t_analysis_id,
                        desk_run_id=desk_run_id,
                        ticker=res['ticker'],
                        recommendation=res['bull_case'].get('overall_sentiment', 'BULLISH'),
                        desk_action=cio_decision.get('action'),
                        decision="FOLLOWED" if execute else "WATCH",
                        decision_notes=cio_decision.get('rationale'),
                        action_taken=cio_decision.get('action') if execute else "NONE",
                        position_size=cio_decision.get('target_size_usd', 0)
                    )
            logger.info(f"📊 Audit trail persisted. Run ID: {desk_run_id}")
        except Exception as e:
            logger.warning(f"⚠️ Could not persist CIO decision to DB: {e}")

        logger.info(f"✅ CIO Decision: {cio_decision.get('action')} {cio_decision.get('selected_ticker')}")
        logger.info(f"   Rationale: {cio_decision.get('rationale')}")

        # ========================================================================
        # STEP 5: EXECUTION
        # ========================================================================
        execution_result = None
        selected_ticker = cio_decision.get('selected_ticker')
        
        if execute and cio_decision.get('action') == "BUY" and selected_ticker != "NONE":
            logger.info(f"\n💼 STEP 5: EXECUTION")
            executioner_path = os.path.join(subagents_dir, "executioner", "agent.py")
            exec_mod = load_mod("executioner", executioner_path)
            
            # Use size from CIO (already checked by guardrails)
            final_size = cio_decision.get('target_size_usd', capital)
            # Rough estimate for quantity
            quantity = max(1, int(final_size / 150)) 
            
            execution_result = exec_mod.execute_trade(selected_ticker, "BUY", quantity)
            logger.info(f"✅ Trade executed: {execution_result}")

        return {
            "theme": theme,
            "cio_decision": cio_decision,
            "portfolio_state": portfolio_state,
            "execution_result": execution_result
        }

    except Exception as e:
        logger.error(f"❌ Error during workflow: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def determine_investment_action(
    hypothesis: Dict,
    bull_case: Dict,
    bear_case: Dict,
    risk_analysis: Dict,
    sentiment_score: float
) -> str:
    """Determine investment action based on all inputs.

    Args:
        hypothesis: Investment hypothesis
        bull_case: Bullish analysis
        bear_case: Bearish analysis
        risk_analysis: Risk assessment
        sentiment_score: Sentiment score (-1 to 1)

    Returns:
        Action: "BUY", "HOLD", or "SELL"
    """
    # Simple scoring system
    score = 0

    # Hypothesis score
    thesis = hypothesis.get('thesis', '').lower()
    if 'bullish' in thesis:
        score += 2
    elif 'bearish' in thesis:
        score -= 2

    # Sentiment score (scaled)
    score += sentiment_score * 2

    # Bull/Bear case strength
    bull_strength = len(bull_case.get('arguments', []))
    bear_strength = len(bear_case.get('arguments', []))
    score += (bull_strength - bear_strength) * 0.5

    # Risk assessment
    risk_score = risk_analysis.get('risk_score', '').lower()
    if risk_score in ['low', 'medium']:
        score += 1
    elif risk_score == 'high':
        score -= 1

    # Determine action
    if score >= 2:
        return "BUY"
    elif score <= -2:
        return "SELL"
    else:
        return "HOLD"

def calculate_quantity(capital: float, symbol: str, risk_analysis: Dict) -> int:
    """Calculate position quantity based on capital and risk analysis.

    Args:
        capital: Available capital
        symbol: Ticker symbol
        risk_analysis: Risk assessment from Risk Manager

    Returns:
        Number of shares to buy
    """
    # Get position size recommendation
    position_size = risk_analysis.get('position_size_recommendation', '').lower()

    if 'appropriate' in position_size or 'medium' in position_size:
        # Use 100% of capital
        position_capital = capital
    elif 'conservative' in position_size or 'small' in position_size:
        # Use 50% of capital
        position_capital = capital * 0.5
    elif 'aggressive' in position_size or 'large' in position_size:
        # Use 150% of capital (margin)
        position_capital = capital * 1.5
    else:
        # Default to 100%
        position_capital = capital

    # Assume $150 per share (should be replaced with real price)
    estimated_price = 150
    quantity = int(position_capital / estimated_price)

    return max(1, quantity)  # At least 1 share

def main():
    """Main entry point for Orchestrator CLI."""
    parser = argparse.ArgumentParser(
        description="Orchestrate complete investment workflow using all subagents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze AI infrastructure stocks with $5000
  python agent.py "AI infrastructure" --capital 5000

  # Analyze EV stocks with $10000 and execute trade
  python agent.py "electric vehicles" --capital 10000 --execute

  # Enable AUTOPILOT MODE (automatic execution)
  AUTOPILOT_MODE=on python agent.py "renewable energy" --capital 2000

Notes:
  - AUTOPILOT_MODE=on enables automatic execution in Paper Trading
  - News ingestion is skipped if data exists from < 4 hours ago
        """
    )

    parser.add_argument("theme", type=str, help="Investment theme to explore")
    parser.add_argument("--capital", type=float, default=1000.0, help="Capital to allocate (default: $1000)")
    parser.add_argument("--execute", action="store_true", help="Actually execute the trade (default: False)")

    args = parser.parse_args()

    # Check if AUTOPILOT_MODE is enabled
    autopilot_mode = os.getenv("AUTOPILOT_MODE", "off").lower() == "on"
    if autopilot_mode:
        print("🤖 AUTOPILOT MODE: ON - Automatic execution enabled\n")

    result = orchestrate_investment_workflow(args.theme, args.capital, args.execute)

    if "error" in result:
        print(f"\n❌ ERROR: {result['error']}")
        return 1

    # Display results
    print("\n" + "="*70)
    print("📊 WORKFLOW RESULTS")
    print("="*70)

    cio_decision = result.get('cio_decision', {})
    portfolio_state = result.get('portfolio_state', {})

    print(f"\n🧠 CIO Decision:")
    print(f"   Ticker: {cio_decision.get('selected_ticker')}")
    print(f"   Action: {cio_decision.get('action')}")
    print(f"   Target Size: ${cio_decision.get('target_size_usd', 0):,.2f}")

    if 'guardrail_check' in cio_decision:
        guardrail = cio_decision['guardrail_check']
        print(f"   Guardrail: {guardrail.get('is_valid')} - ${guardrail.get('allowed_size_usd', 0):,.2f}")

    print(f"\n💰 Portfolio:")
    print(f"   Equity: ${portfolio_state.get('equity', 0):,.2f}")
    print(f"   Cash: ${portfolio_state.get('cash', 0):,.2f}")
    print(f"   Exposure: {portfolio_state.get('total_exposure_pct', 0)*100:.1f}%")

    if result.get('execution_result'):
        print(f"\n💼 EXECUTION RESULT:")
        print(f"   {result['execution_result']}")

    print("="*70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
