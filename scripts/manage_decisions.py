#!/usr/bin/env python3
"""
Investment Decision Management

Gestiona decisiones basadas en recomendaciones de la mesa:
- Ver recomendaciones pendientes
- Tomar decisiones (SEGUIR/IGNORAR/MODIFICAR)
- Registrar acciones ejecutadas
- Actualizar resultados
- Ver historial y performance

Uso:
    python manage_decisions.py list-pending
    python manage_decisions.py decide --ticker-analysis-id 1 --decision FOLLOWED --action BOUGHT --size 100 --price 75.50
    python manage_decisions.py outcome --decision-id 1 --exit-price 78.50
    python manage_decisions.py history --ticker COP
    python manage_decisions.py performance
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import argparse
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('investment_decisions.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from trading_mvp.core.db_investment_tracking import (
    create_investment_tracking_tables,
    record_decision,
    update_decision_outcome,
    get_decision_history,
    get_performance_stats,
    get_audit_trail
)


def list_pending_recommendations(limit: int = 20):
    """List pending ticker analyses that need decisions.

    Args:
        limit: Max records to show
    """

    from trading_mvp.core.db_manager import get_connection

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    t.id,
                    t.ticker,
                    t.recommendation,
                    t.rationale,
                    t.analysis_timestamp,
                    t.avg_confidence,
                    t.related_news_count,
                    dr.watchlist_name,
                    dr.overall_sentiment as desk_sentiment,
                    d.id as decision_id
                FROM ticker_analyses t
                JOIN investment_desk_runs dr ON t.desk_run_id = dr.id
                LEFT JOIN investment_decisions d ON t.id = d.ticker_analysis_id
                WHERE d.id IS NULL
                ORDER BY t.analysis_timestamp DESC
                LIMIT %s
            """, (limit,))

            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        print("\n✅ No pending recommendations found")
        return

    print()
    print("="*70)
    print("📋 PENDING RECOMMENDATIONS")
    print("="*70)
    print()

    for row in rows:
        (analysis_id, ticker, recommendation, rationale, timestamp, confidence,
         news_count, watchlist, desk_sentiment, decision_id) = row

        emoji = {
            'BULLISH': '🚀',
            'BEARISH': '📉',
            'CAUTIOUS': '⚠️',
            'NEUTRAL': '😐'
        }.get(recommendation, '•')

        print(f"{emoji} {ticker} - {recommendation}")
        print(f"   Analysis ID: {analysis_id}")
        print(f"   Timestamp: {timestamp}")
        print(f"   Watchlist: {watchlist}")
        print(f"   Desk Sentiment: {desk_sentiment}")
        print(f"   Confidence: {confidence:.2f} | News: {news_count}")
        print(f"   Rationale: {rationale[:100]}...")
        print()

    print("="*70)
    print(f"\n💡 To decide on a recommendation:")
    print(f"   python manage_decisions.py decide --ticker-analysis-id <ID> --decision <FOLLOWED|IGNORED|MODIFIED> --action <BOUGHT|SOLD|HELD|NONE> [--size <size>] [--price <price>]")


def make_decision(
    ticker_analysis_id: int,
    decision: str,
    action: str = None,
    notes: str = None,
    size: float = None,
    entry_price: float = None
):
    """Make a decision on a ticker analysis.

    Args:
        ticker_analysis_id: Ticker analysis ID
        decision: FOLLOWED, IGNORED, MODIFIED
        action: BOUGHT, SOLD, HELD, HEDGED, NONE
        notes: Decision notes
        size: Position size (if executed)
        entry_price: Entry price (if executed)
    """

    from trading_mvp.core.db_manager import get_connection

    # Get ticker analysis details
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    t.ticker,
                    t.recommendation,
                    t.desk_run_id,
                    dr.overall_sentiment
        FROM ticker_analyses t
        JOIN investment_desk_runs dr ON t.desk_run_id = dr.id
        WHERE t.id = %s
    """, (ticker_analysis_id,))

            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        print(f"❌ Ticker analysis {ticker_analysis_id} not found")
        return

    ticker, recommendation, desk_run_id, desk_sentiment = row

    # Determine desk action
    desk_action_map = {
        'BULLISH': 'BUY',
        'BEARISH': 'AVOID',
        'CAUTIOUS': 'WATCH',
        'NEUTRAL': 'HOLD'
    }
    desk_action = desk_action_map.get(recommendation, 'WATCH')

    # Record decision
    decision_id = record_decision(
        ticker_analysis_id=ticker_analysis_id,
        desk_run_id=desk_run_id,
        ticker=ticker,
        recommendation=recommendation,
        desk_action=desk_action,
        decision=decision,
        decision_notes=notes,
        action_taken=action,
        position_size=size,
        entry_price=entry_price
    )

    if decision_id:
        print()
        print("="*70)
        print("✅ DECISION RECORDED")
        print("="*70)
        print()
        print(f"Ticker: {ticker}")
        print(f"Recommendation: {recommendation} ({desk_action})")
        print(f"Your Decision: {decision}")
        print(f"Action Taken: {action or 'None'}")
        if size:
            print(f"Position Size: {size}")
        if entry_price:
            print(f"Entry Price: ${entry_price:.2f}")
        print(f"Decision ID: {decision_id}")
        print()
        print("="*70)
        print(f"\n💡 To update outcome later:")
        print(f"   python manage_decisions.py outcome --decision-id {decision_id} --exit-price <PRICE>")
    else:
        print(f"❌ Failed to record decision")


def record_outcome(decision_id: int, exit_price: float, notes: str = None, rating: int = None):
    """Record the outcome of a decision.

    Args:
        decision_id: Decision ID
        exit_price: Exit price
        notes: Outcome notes
        rating: Rating 1-5
    """

    from trading_mvp.core.db_manager import get_connection

    # Get decision details
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    d.ticker,
                    d.entry_price,
                    d.position_size,
                    d.recommendation,
                    t.avg_confidence
                FROM investment_decisions d
                JOIN ticker_analyses t ON d.ticker_analysis_id = t.id
                WHERE d.id = %s
            """, (decision_id,))

            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        print(f"❌ Decision {decision_id} not found")
        return

    ticker, entry_price, position_size, recommendation, confidence = row

    if not entry_price:
        print(f"❌ This decision has no entry price recorded")
        conn.close()
        return

    # Calculate P&L
    if position_size:
        profit_loss = (exit_price - entry_price) * position_size
        profit_loss_pct = ((exit_price - entry_price) / entry_price) * 100
    else:
        profit_loss = exit_price - entry_price
        profit_loss_pct = ((exit_price - entry_price) / entry_price) * 100

    # Determine if recommendation was correct
    actual_outcome = "PROFIT" if profit_loss > 0 else ("LOSS" if profit_loss < 0 else "BREAKEVEN")
    was_correct = (recommendation == "BULLISH" and profit_loss > 0) or \
                  (recommendation == "BEARISH" and profit_loss < 0)

    # Update outcome
    success = update_decision_outcome(
        decision_id=decision_id,
        exit_price=exit_price,
        profit_loss=profit_loss,
        profit_loss_pct=profit_loss_pct,
        status='CLOSED',
        was_correct=was_correct,
        actual_outcome=actual_outcome,
        outcome_notes=notes,
        rating=rating
    )

    conn.close()

    if success:
        print()
        print("="*70)
        print("✅ OUTCOME RECORDED")
        print("="*70)
        print()
        print(f"Ticker: {ticker}")
        print(f"Entry: ${entry_price:.2f} → Exit: ${exit_price:.2f}")
        print(f"P&L: ${profit_loss:.2f} ({profit_loss_pct:+.2f}%)")
        print(f"Outcome: {actual_outcome}")
        if was_correct:
            print(f"✅ Recommendation was CORRECT")
        else:
            print(f"❌ Recommendation was INCORRECT")
        if rating:
            print(f"Rating: {rating}/5 ⭐")
        print()
        print("="*70)
    else:
        print(f"❌ Failed to record outcome")


def show_history(ticker: str = None, limit: int = 20):
    """Show decision history.

    Args:
        ticker: Filter by ticker (optional)
        limit: Max records to show
    """

    decisions = get_decision_history(ticker=ticker, limit=limit)

    if not decisions:
        print(f"\n✅ No decision history found" + (f" for {ticker}" if ticker else ""))
        return

    print()
    print("="*70)
    print(f"📊 DECISION HISTORY" + (f" - {ticker}" if ticker else ""))
    print("="*70)
    print()

    for d in decisions:
        ticker = d['ticker']
        recommendation = d['ticker_recommendation']
        decision = d['decision']
        action = d['action_taken'] or 'None'
        status = d['status']

        emoji_emoji = {
            'BULLISH': '🚀',
            'BEARISH': '📉',
            'CAUTIOUS': '⚠️',
            'NEUTRAL': '😐'
        }.get(recommendation, '•')

        decision_emoji = {
            'FOLLOWED': '✅',
            'IGNORED': '❌',
            'MODIFIED': '🔄'
        }.get(decision, '•')

        status_emoji = {
            'PENDING': '⏳',
            'OPEN': '📈',
            'CLOSED': '✓',
            'CANCELLED': '🚫'
        }.get(status, '•')

        print(f"{emoji_emoji} {ticker} - {recommendation}")
        print(f"   Decision: {decision_emoji} {decision} | Action: {action}")
        print(f"   Status: {status_emoji} {status}")

        if d['entry_price']:
            print(f"   Entry: ${d['entry_price']:.2f}")
            if d['position_size']:
                print(f"   Size: {d['position_size']}")
            if d['exit_price']:
                print(f"   Exit: ${d['exit_price']:.2f}")
                if d['profit_loss_pct'] is not None:
                    print(f"   P&L: {d['profit_loss_pct']:+.2f}%")

        print(f"   Date: {d['decision_timestamp']}")
        print()

    print("="*70)


def show_performance(ticker: str = None):
    """Show performance statistics.

    Args:
        ticker: Filter by ticker (optional)
    """

    stats = get_performance_stats(ticker=ticker)

    print()
    print("="*70)
    print(f"📈 PERFORMANCE STATS" + (f" - {ticker}" if ticker else ""))
    print("="*70)
    print()

    print(f"Total Decisions: {stats['total_decisions']}")
    print(f"Closed Decisions: {stats['closed_decisions']}")
    print(f"Positions Bought: {stats['bought_count']}")
    print()

    if stats['total_pl'] is not None:
        print(f"Total P&L: ${stats['total_pl']:.2f}")

    if stats['avg_pl_pct'] is not None:
        print(f"Avg P&L %: {stats['avg_pl_pct']:+.2f}%")

    if stats['correct_recommendations'] or stats['incorrect_recommendations']:
        total_rec = stats['correct_recommendations'] + stats['incorrect_recommendations']
        if total_rec > 0:
            accuracy = (stats['correct_recommendations'] / total_rec) * 100
            print(f"Recommendation Accuracy: {accuracy:.1f}%")
            print(f"  Correct: {stats['correct_recommendations']}/{total_rec}")

    if stats['avg_rating'] is not None:
        print(f"Avg Rating: {stats['avg_rating']:.1f}/5 ⭐")

    print()
    print("="*70)


def show_audit_trail(ticker: str, hours_back: int = 48):
    """Show full audit trail for a ticker.

    Args:
        ticker: Ticker symbol
        hours_back: Hours to look back
    """

    trail = get_audit_trail(ticker=ticker, hours_back=hours_back)

    if not trail:
        print(f"\n✅ No audit trail found for {ticker} in last {hours_back} hours")
        return

    print()
    print("="*70)
    print(f"🔍 AUDIT TRAIL: {ticker} (Last {hours_back} hours)")
    print("="*70)
    print()

    for entry in trail:
        print(f"📅 Analysis: {entry['analysis_timestamp']}")
        print(f"   Desk Sentiment: {entry['overall_sentiment']}")
        print(f"   Ticker Recommendation: {entry['recommendation']}")
        print(f"   Confidence: {entry['avg_confidence']:.2f}")
        print(f"   News Analyzed: {entry['related_news_count']}")
        print(f"   Entities Found: {entry['unique_entities_found']}")
        print()

        if entry.get('top_risks'):
            print("   ⚠️  Top Risks:")
            risks = entry['top_risks'][:3] if isinstance(entry['top_risks'], list) else []
            for risk in risks:
                if isinstance(risk, dict):
                    print(f"      • {risk.get('entity_name', 'N/A')} ({risk.get('overall_impact', 'N/A')})")

        if entry.get('top_opportunities'):
            print("   🚀 Top Opportunities:")
            opps = entry['top_opportunities'][:3] if isinstance(entry['top_opportunities'], list) else []
            for opp in opps:
                if isinstance(opp, dict):
                    print(f"      • {opp.get('entity_name', 'N/A')} ({opp.get('overall_impact', 'N/A')})")

        print()

        if entry['decision_id']:
            print(f"   📝 Decision ID: {entry['decision_id']}")
            print(f"   Decision: {entry['decision']}")
            print(f"   Action: {entry['action_taken'] or 'None'}")

            if entry['entry_price']:
                print(f"   Entry Price: ${entry['entry_price']:.2f}")
                if entry['position_size']:
                    print(f"   Position Size: {entry['position_size']}")

            if entry['exit_price']:
                print(f"   Exit Price: ${entry['exit_price']:.2f}")
                if entry['profit_loss_pct'] is not None:
                    print(f"   P&L: {entry['profit_loss_pct']:+.2f}%")

            print(f"   Status: {entry['status']}")
        else:
            print("   📝 No decision recorded yet")

        print()
        print("-" * 70)
        print()

    print("="*70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Investment Decision Management')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # List pending recommendations
    subparsers.add_parser('list-pending', help='List pending recommendations')

    # Make a decision
    decide_parser = subparsers.add_parser('decide', help='Make a decision on a recommendation')
    decide_parser.add_argument('--ticker-analysis-id', type=int, required=True, help='Ticker analysis ID')
    decide_parser.add_argument('--decision', type=str, required=True, choices=['FOLLOWED', 'IGNORED', 'MODIFIED'], help='Decision')
    decide_parser.add_argument('--action', type=str, choices=['BOUGHT', 'SOLD', 'HELD', 'HEDGED', 'NONE'], help='Action taken')
    decide_parser.add_argument('--notes', type=str, help='Decision notes')
    decide_parser.add_argument('--size', type=float, help='Position size')
    decide_parser.add_argument('--price', type=float, help='Entry price')

    # Record outcome
    outcome_parser = subparsers.add_parser('outcome', help='Record outcome of a decision')
    outcome_parser.add_argument('--decision-id', type=int, required=True, help='Decision ID')
    outcome_parser.add_argument('--exit-price', type=float, required=True, help='Exit price')
    outcome_parser.add_argument('--notes', type=str, help='Outcome notes')
    outcome_parser.add_argument('--rating', type=int, choices=[1,2,3,4,5], help='Rating 1-5')

    # Show history
    history_parser = subparsers.add_parser('history', help='Show decision history')
    history_parser.add_argument('--ticker', type=str, help='Filter by ticker')

    # Show performance
    perf_parser = subparsers.add_parser('performance', help='Show performance statistics')
    perf_parser.add_argument('--ticker', type=str, help='Filter by ticker')

    # Show audit trail
    audit_parser = subparsers.add_parser('audit', help='Show audit trail')
    audit_parser.add_argument('--ticker', type=str, required=True, help='Ticker symbol')
    audit_parser.add_argument('--hours-back', type=int, default=48, help='Hours to look back')

    args = parser.parse_args()

    # Ensure tables exist
    create_investment_tracking_tables()

    # Execute command
    if args.command == 'list-pending':
        list_pending_recommendations()
    elif args.command == 'decide':
        make_decision(
            ticker_analysis_id=args.ticker_analysis_id,
            decision=args.decision,
            action=args.action,
            notes=args.notes,
            size=args.size,
            entry_price=args.price
        )
    elif args.command == 'outcome':
        record_outcome(
            decision_id=args.decision_id,
            exit_price=args.exit_price,
            notes=args.notes,
            rating=args.rating
        )
    elif args.command == 'history':
        show_history(ticker=args.ticker)
    elif args.command == 'performance':
        show_performance(ticker=args.ticker)
    elif args.command == 'audit':
        show_audit_trail(ticker=args.ticker, hours_back=args.hours_back)
    else:
        parser.print_help()
