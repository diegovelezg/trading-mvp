#!/usr/bin/env python3
"""
Investment Desk - Complete Watchlist Analysis

Ejecuta la mesa de inversiones completa:
1. Analiza TODOS los tickers en la watchlist
2. Compara resultados entre tickers
3. Genera recomendaciones consolidadas
4. Presenta ranking y sugerencias de acción

Uso:
    python run_investment_desk.py --watchlist-id 3
    python run_investment_desk.py --watchlist-name "Oil & Energy Watchlist"
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import logging
from datetime import datetime
from typing import List, Dict, Optional
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('investment_desk.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up environment
os.environ['ALPACA_PAPER_API_KEY'] = 'YOUR_ALPACA_PAPER_API_KEY'
os.environ['PAPER_API_SECRET'] = 'YOUR_ALPACA_SECRET_KEY'
os.environ['SERPAPI_API_KEY'] = 'YOUR_SERPAPI_API_KEY'
os.environ['GEMINI_API_KEY'] = 'AIzaSyCutHRoCMkN02KhsVYATzu5XRPjboQZxnc'
os.environ['GEMINI_API_MODEL_01'] = 'gemini-3.1-flash-lite-preview'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.claude', 'subagents'))

from trading_mvp.core.db_watchlist import (
    get_watchlist,
    get_watchlist_tickers,
    get_active_watchlists
)
from trading_mvp.core.db_investment_tracking import (
    create_investment_tracking_tables,
    save_desk_run,
    save_ticker_analysis,
    record_decision
)
from trading_mvp.agents.decision_agent import (
    DecisionAgent,
    DecisionConfig,
    DEFAULT_CONFIG
)

# Import analyze_ticker function
import importlib.util
spec = importlib.util.spec_from_file_location("analyze_ticker", "analyze_ticker.py")
analyze_ticker_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyze_ticker_module)


def run_investment_desk(watchlist_id: int = None, watchlist_name: str = None, hours_back: int = 48) -> Dict:
    """Run complete investment desk analysis on a watchlist.

    Args:
        watchlist_id: Watchlist ID (optional, use watchlist_name instead)
        watchlist_name: Watchlist name (optional, use watchlist_id instead)
        hours_back: Hours to look back for news

    Returns:
        Complete investment desk analysis
    """

    logger.info("="*70)
    logger.info("🏛️  INVESTMENT DESK - COMPLETE ANALYSIS")
    logger.info("="*70)
    logger.info("")

    start_time = datetime.now()

    # 0. Ensure tracking tables exist
    create_investment_tracking_tables()

    # 1. Get watchlist
    if watchlist_id:
        watchlist = get_watchlist(watchlist_id)
        if not watchlist:
            logger.error(f"❌ Watchlist ID {watchlist_id} not found")
            return {"success": False, "error": "Watchlist not found"}
    elif watchlist_name:
        # Find by name
        watchlists = get_active_watchlists()
        watchlist = next((wl for wl in watchlists if wl['name'] == watchlist_name), None)
        if not watchlist:
            logger.error(f"❌ Watchlist '{watchlist_name}' not found")
            return {"success": False, "error": "Watchlist not found"}
        watchlist_id = watchlist['id']
    else:
        # Use first active watchlist
        watchlists = get_active_watchlists()
        if not watchlists:
            logger.error("❌ No active watchlists found")
            return {"success": False, "error": "No active watchlists"}
        watchlist = watchlists[0]
        watchlist_id = watchlist['id']

    logger.info(f"📋 Watchlist: {watchlist['name']}")
    logger.info(f"   Description: {watchlist['description']}")
    logger.info("")

    # 2. Get tickers
    logger.info(f"📊 Loading tickers...")
    tickers_data = get_watchlist_tickers(watchlist_id)
    tickers = [t['ticker'] for t in tickers_data]

    if not tickers:
        logger.error(f"❌ No tickers found in watchlist")
        return {"success": False, "error": "No tickers in watchlist"}

    logger.info(f"   ✅ Found {len(tickers)} tickers: {', '.join(tickers)}")
    logger.info("")

    # 3. Analyze each ticker
    logger.info(f"🔍 Analyzing tickers...")
    logger.info("")

    ticker_results = []
    failed_tickers = []

    for i, ticker in enumerate(tickers, 1):
        logger.info(f"[{i}/{len(tickers)}] Analyzing {ticker}...")

        try:
            result = analyze_ticker_module.analyze_ticker(ticker, hours_back=hours_back)
            if result.get('success'):
                ticker_results.append(result)
                logger.info(f"   ✅ {ticker}: {result['recommendation']}")
            else:
                failed_tickers.append(ticker)
                logger.warning(f"   ⚠️  {ticker}: Analysis failed")
        except Exception as e:
            failed_tickers.append(ticker)
            logger.error(f"   ❌ {ticker}: {e}")

        logger.info("")

    # 4. Aggregate and compare results
    logger.info(f"📊 Aggregating results...")

    # Group by recommendation
    bullish = [t for t in ticker_results if t['recommendation'] == 'BULLISH']
    bearish = [t for t in ticker_results if t['recommendation'] == 'BEARISH']
    cautious = [t for t in ticker_results if t['recommendation'] == 'CAUTIOUS']
    neutral = [t for t in ticker_results if t['recommendation'] == 'NEUTRAL']

    # Sort by sentiment strength
    bullish.sort(key=lambda x: x['positive_ratio'], reverse=True)
    bearish.sort(key=lambda x: x['negative_ratio'], reverse=True)
    cautious.sort(key=lambda x: -x['positive_ratio'] if x['positive_ratio'] > x['negative_ratio'] else x['negative_ratio'])

    # Calculate aggregate metrics
    if ticker_results:
        avg_confidence = sum(t['avg_confidence'] for t in ticker_results) / len(ticker_results)
        avg_negative = sum(t['negative_ratio'] for t in ticker_results) / len(ticker_results)
        avg_positive = sum(t['positive_ratio'] for t in ticker_results) / len(ticker_results)
        total_news = sum(t['related_news_count'] for t in ticker_results)
        total_entities = sum(t['unique_entities_found'] for t in ticker_results)
    else:
        avg_confidence = 0
        avg_negative = 0
        avg_positive = 0
        total_news = 0
        total_entities = 0

    logger.info(f"   ✅ Aggregated {len(ticker_results)} ticker analyses")
    logger.info("")

    # 5. Generate desk recommendations
    logger.info(f"💡 Generating desk recommendations...")

    desk_recommendations = []

    # Top picks (BULLISH with high confidence)
    top_picks = [t for t in bullish if t['avg_confidence'] >= 0.8][:3]
    if top_picks:
        desk_recommendations.append({
            'action': 'BUY',
            'tickers': [t['ticker'] for t in top_picks],
            'rationale': f"Strong bullish sentiment with high confidence. Top pick: {top_picks[0]['ticker']} ({top_picks[0]['positive_ratio']:.1%} positive)"
        })

    # Avoid (BEARISH with high confidence)
    avoid = [t for t in bearish if t['avg_confidence'] >= 0.8]
    if avoid:
        desk_recommendations.append({
            'action': 'AVOID',
            'tickers': [t['ticker'] for t in avoid],
            'rationale': f"High bearish pressure. Reduce exposure or hedge."
        })

    # Watch (CAUTIOUS with mixed signals)
    watch_list = cautious[:3]
    if watch_list:
        desk_recommendations.append({
            'action': 'WATCH',
            'tickers': [t['ticker'] for t in watch_list],
            'rationale': "Mixed signals. Wait for clearer direction before committing."
        })

    # Overall desk sentiment
    if len(bullish) > len(bearish) and avg_positive > avg_negative:
        overall_sentiment = "BULLISH"
        desk_outlook = "Favorable conditions across most tickers. Consider increasing exposure."
    elif len(bearish) > len(bullish) and avg_negative > avg_positive:
        overall_sentiment = "BEARISH"
        desk_outlook = "Negative sentiment dominates. Consider reducing risk or hedging."
    elif avg_positive > avg_negative:
        overall_sentiment = "CAUTIOUSLY BULLISH"
        desk_outlook = "Moderate positive bias. Selective opportunities."
    elif avg_negative > avg_positive:
        overall_sentiment = "CAUTIOUSLY BEARISH"
        desk_outlook = "Moderate negative bias. Defensive posture recommended."
    else:
        overall_sentiment = "NEUTRAL"
        desk_outlook = "No clear directional bias. Maintain balanced approach."

    logger.info(f"   ✅ Overall desk sentiment: {overall_sentiment}")
    logger.info("")

    # 6. Compile final report
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    desk_analysis = {
        'success': True,
        'watchlist': {
            'id': watchlist_id,
            'name': watchlist['name'],
            'description': watchlist['description']
        },
        'analysis_timestamp': datetime.now().isoformat(),
        'time_window_hours': hours_back,
        'duration_seconds': round(duration, 1),

        # Ticker breakdown
        'total_tickers': len(tickers),
        'analyzed_tickers': len(ticker_results),
        'failed_tickers': failed_tickers,

        # Aggregate metrics
        'avg_confidence': round(avg_confidence, 2),
        'avg_negative_ratio': round(avg_negative, 2),
        'avg_positive_ratio': round(avg_positive, 2),
        'total_news_analyzed': total_news,
        'total_entities_found': total_entities,

        # Recommendation breakdown
        'bullish_count': len(bullish),
        'bearish_count': len(bearish),
        'cautious_count': len(cautious),
        'neutral_count': len(neutral),

        # Ticker results
        'bullish_tickers': bullish,
        'bearish_tickers': bearish,
        'cautious_tickers': cautious,
        'neutral_tickers': neutral,

        # Desk recommendations
        'overall_sentiment': overall_sentiment,
        'desk_outlook': desk_outlook,
        'recommendations': desk_recommendations,

        # Individual results
        'ticker_results': ticker_results
    }

    # 7. SAVE TO DATABASE (AUDIT TRAIL)
    logger.info("")
    logger.info(f"💾 Saving audit trail to database...")

    # Save desk run
    desk_run_id = save_desk_run(desk_analysis)

    if desk_run_id:
        logger.info(f"   ✅ Desk run saved: ID {desk_run_id}")

        # Save each ticker analysis
        ticker_analysis_ids = {}
        for ticker_result in ticker_results:
            ticker_analysis_id = save_ticker_analysis(ticker_result, desk_run_id)
            if ticker_analysis_id:
                ticker_analysis_ids[ticker_result['ticker']] = ticker_analysis_id
                logger.info(f"   ✅ Saved ticker analysis for {ticker_result['ticker']}: ID {ticker_analysis_id}")

        # Add IDs to desk_analysis for reference
        desk_analysis['desk_run_id'] = desk_run_id
        desk_analysis['ticker_analysis_ids'] = ticker_analysis_ids

        logger.info(f"   ✅ Audit trail complete: {len(ticker_analysis_ids)} ticker analyses saved")
    else:
        logger.error(f"   ❌ Failed to save desk run")
        desk_analysis['desk_run_id'] = None
        desk_analysis['ticker_analysis_ids'] = {}

    logger.info("")

    # 8. DECISION AGENT - Process recommendations (if enabled)
    logger.info(f"🤖 Initializing Decision Agent...")

    # Check if autopilot is enabled via environment
    autopilot_mode = os.getenv("AUTOPILOT_MODE", "off").lower() == "on"

    if autopilot_mode or True:  # Always run agent (user can toggle with env var)
        decision_config = DecisionConfig(autopilot_enabled=autopilot_mode)
        decision_agent = DecisionAgent(config=decision_config)

        # Process recommendations
        agent_decisions = decision_agent.process_desk_recommendations(
            desk_analysis=desk_analysis,
            portfolio_context={}  # TODO: Add portfolio context
        )

        desk_analysis['agent_decisions'] = agent_decisions

        # Record decisions to database if in autopilot mode
        if autopilot_mode and desk_run_id:
            logger.info("")
            logger.info(f"💾 Recording agent decisions to database...")

            for decision in agent_decisions:
                ticker_analysis_id = ticker_analysis_ids.get(decision['ticker'])

                if ticker_analysis_id and decision['action'] != 'NONE':
                    decision_id = record_decision(
                        ticker_analysis_id=ticker_analysis_id,
                        desk_run_id=desk_run_id,
                        ticker=decision['ticker'],
                        recommendation=decision['original_recommendation'],
                        desk_action='BUY' if decision['action'] == 'BOUGHT' else 'AVOID',
                        decision=decision['decision'],
                        decision_notes=decision['rationale'],
                        action_taken=decision['action'],
                        position_size=decision.get('position_size'),
                        entry_price=decision.get('entry_price'),
                        alpaca_order_id=decision.get('order_id')
                    )

                    if decision_id:
                        logger.info(f"   ✅ Recorded decision for {decision['ticker']}: {decision['action']}")

            logger.info("")
    else:
        logger.info("   ⚠️  Decision Agent disabled (set AUTOPILOT_MODE=on to enable)")
        desk_analysis['agent_decisions'] = []

    logger.info("="*70)
    logger.info(f"✅ INVESTMENT DESK ANALYSIS COMPLETE")
    logger.info(f"   Duration: {duration:.1f}s")
    logger.info(f"   Tickers analyzed: {len(ticker_results)}/{len(tickers)}")
    logger.info(f"   Overall sentiment: {overall_sentiment}")
    if desk_run_id:
        logger.info(f"   📝 Audit trail: Desk Run ID {desk_run_id}")
    logger.info("="*70)

    return desk_analysis


def print_investment_desk_report(desk_analysis: Dict):
    """Print complete investment desk report.

    Args:
        desk_analysis: Analysis dictionary from run_investment_desk()
    """

    if not desk_analysis.get('success'):
        print(f"❌ Analysis failed: {desk_analysis.get('error', 'Unknown error')}")
        return

    print()
    print("="*70)
    print("🏛️  INVESTMENT DESK - COMPLETE REPORT")
    print("="*70)
    print()

    # Header
    watchlist = desk_analysis['watchlist']
    print(f"📋 WATCHLIST: {watchlist['name']}")
    print(f"   {watchlist['description']}")
    print()
    print(f"⏰ Analysis Time: {desk_analysis['analysis_timestamp']}")
    print(f"📊 Time Window: Last {desk_analysis['time_window_hours']} hours")
    print(f"⚡ Duration: {desk_analysis['duration_seconds']}s")
    print()

    # Overall desk sentiment
    print(f"💡 OVERALL DESK SENTIMENT: {desk_analysis['overall_sentiment']}")
    print(f"   {desk_analysis['desk_outlook']}")
    print()

    # Aggregate metrics
    print("📊 AGGREGATE METRICS:")
    print(f"   • Tickers analyzed: {desk_analysis['analyzed_tickers']}/{desk_analysis['total_tickers']}")
    print(f"   • Total news analyzed: {desk_analysis['total_news_analyzed']}")
    print(f"   • Total entities found: {desk_analysis['total_entities_found']}")
    print(f"   • Average confidence: {desk_analysis['avg_confidence']:.2f}")
    print(f"   • Average negative ratio: {desk_analysis['avg_negative_ratio']:.1%}")
    print(f"   • Average positive ratio: {desk_analysis['avg_positive_ratio']:.1%}")
    print()

    # Recommendation breakdown
    print("📈 RECOMMENDATION BREAKDOWN:")
    print(f"   • 🚀 BULLISH: {desk_analysis['bullish_count']} tickers")
    print(f"   • ⚠️  CAUTIOUS: {desk_analysis['cautious_count']} tickers")
    print(f"   • 📉 BEARISH: {desk_analysis['bearish_count']} tickers")
    print(f"   • 😐 NEUTRAL: {desk_analysis['neutral_count']} tickers")
    print()

    # Desk recommendations
    if desk_analysis.get('recommendations'):
        print("🎯 DESK RECOMMENDATIONS:")
        for rec in desk_analysis['recommendations']:
            action_emoji = {
                'BUY': '✅',
                'AVOID': '❌',
                'WATCH': '👀',
                'HOLD': '⏸️'
            }.get(rec['action'], '•')

            print(f"   {action_emoji} {rec['action']}: {', '.join(rec['tickers'])}")
            print(f"      {rec['rationale']}")
        print()

    # Top picks (BULLISH)
    if desk_analysis.get('bullish_tickers'):
        print("🚀 TOP PICKS (BULLISH):")
        for i, ticker in enumerate(desk_analysis['bullish_tickers'][:5], 1):
            print(f"   {i}. {ticker['ticker']}")
            print(f"      Positive: {ticker['positive_ratio']:.1%} | Negative: {ticker['negative_ratio']:.1%} | Conf: {ticker['avg_confidence']:.2f}")
            print(f"      News: {ticker['related_news_count']} | Entities: {ticker['unique_entities_found']}")
            print(f"      Rationale: {ticker['rationale'][:80]}...")
        print()

    # Avoid (BEARISH)
    if desk_analysis.get('bearish_tickers'):
        print("⚠️  AVOID (BEARISH):")
        for i, ticker in enumerate(desk_analysis['bearish_tickers'][:3], 1):
            print(f"   {i}. {ticker['ticker']}")
            print(f"      Negative: {ticker['negative_ratio']:.1%} | Positive: {ticker['positive_ratio']:.1%} | Conf: {ticker['avg_confidence']:.2f}")
            print(f"      News: {ticker['related_news_count']} | Entities: {ticker['unique_entities_found']}")
            print(f"      Rationale: {ticker['rationale'][:80]}...")
        print()

    # Watch (CAUTIOUS)
    if desk_analysis.get('cautious_tickers'):
        print("👀 WATCH (CAUTIOUS):")
        for i, ticker in enumerate(desk_analysis['cautious_tickers'][:5], 1):
            print(f"   {i}. {ticker['ticker']}")
            print(f"      Mixed signals | Conf: {ticker['avg_confidence']:.2f}")
            print(f"      News: {ticker['related_news_count']} | Entities: {ticker['unique_entities_found']}")
        print()

    # Individual ticker summaries
    print("📊 INDIVIDUAL TICKER ANALYSIS:")
    for ticker in desk_analysis['ticker_results']:
        sentiment_emoji = {
            'BULLISH': '🚀',
            'BEARISH': '📉',
            'CAUTIOUS': '⚠️',
            'NEUTRAL': '😐'
        }.get(ticker['recommendation'], '•')

        print(f"   {sentiment_emoji} {ticker['ticker']}: {ticker['recommendation']}")
        print(f"      News: {ticker['related_news_count']} | Entities: {ticker['unique_entities_found']} | Conf: {ticker['avg_confidence']:.2f}")

        # Top risks
        if ticker.get('top_risks'):
            top_risk = ticker['top_risks'][0]
            print(f"      Top risk: {top_risk['entity_name']} ({top_risk['overall_impact']})")

        # Top opportunities
        if ticker.get('top_opportunities'):
            top_opp = ticker['top_opportunities'][0]
            print(f"      Top opportunity: {top_opp['entity_name']} ({top_opp['overall_impact']})")
        print()

    # Agent decisions
    if desk_analysis.get('agent_decisions'):
        print()
        print("="*70)
        print("🤖 DECISION AGENT OUTPUT")
        print("="*70)
        print()

        # Mode indicator
        autopilot_mode = os.getenv("AUTOPILOT_MODE", "off").lower() == "on"
        mode_str = "✈️ AUTOPILOT" if autopilot_mode else "👨‍💼 MANUAL (Suggestions Only)"
        print(f"Mode: {mode_str}")
        print()

        # Group by action
        buy_decisions = [d for d in desk_analysis['agent_decisions'] if d['action'] == 'BOUGHT']
        watch_decisions = [d for d in desk_analysis['agent_decisions'] if d['action'] == 'NONE']
        ignore_decisions = [d for d in desk_analysis['agent_decisions'] if d['decision'] == 'IGNORED']

        if buy_decisions:
            print("✅ BUY DECISIONS:")
            for d in buy_decisions:
                print(f"   {d['ticker']}: ${d.get('position_size', 0):.2f} @ ${d.get('entry_price', 0):.2f}")
                if d.get('stop_loss'):
                    print(f"      Stop: ${d['stop_loss']:.2f} | Target: ${d['take_profit']:.2f}")
                print(f"      Rationale: {d['rationale'][:80]}...")
                print()

        if watch_decisions:
            print("👀 WATCH DECISIONS:")
            for d in watch_decisions:
                if d['decision'] == 'FOLLOWED':
                    print(f"   {d['ticker']}: Monitoring - {d['rationale'][:60]}...")
                    print()

        if ignore_decisions:
            print("⚠️  IGNORED RECOMMENDATIONS:")
            for d in ignore_decisions:
                print(f"   {d['ticker']}: {d['rationale'][:60]}...")
                print()

    print("="*70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Investment Desk Analysis')
    parser.add_argument('--watchlist-id', type=int, help='Watchlist ID')
    parser.add_argument('--watchlist-name', type=str, help='Watchlist name')
    parser.add_argument('--hours-back', type=int, default=48, help='Hours to look back (default: 48)')

    args = parser.parse_args()

    # Run analysis
    result = run_investment_desk(
        watchlist_id=args.watchlist_id,
        watchlist_name=args.watchlist_name,
        hours_back=args.hours_back
    )

    # Print report
    print_investment_desk_report(result)

    # Exit with error code if failed
    if not result.get('success'):
        sys.exit(1)
