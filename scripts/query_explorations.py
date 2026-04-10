# Query Explorations

from trading_mvp.core.dashboard_api_client import get_recent_explorations
import sys

def show_recent_explorations(limit=5):
    """Display recent exploration history with criteria."""
    explorations = get_recent_explorations(limit)

    if not explorations:
        print("No explorations found in database.")
        return

    print(f"\n{'='*80}")
    print(f"📋 RECENT EXPLORATIONS (Last {len(explorations)})")
    print(f"{'='*80}\n")

    for exp in explorations:
        print(f"🔍 Theme: {exp['prompt']}")
        print(f"📊 Criteria: {exp['criteria']}")
        print(f"🎯 Tickers: {exp['tickers']}")
        print(f"💭 Reasoning: {exp['reasoning'][:100]}..." if len(exp['reasoning']) > 100 else f"💭 Reasoning: {exp['reasoning']}")
        print(f"⏰ Timestamp: {exp['timestamp']}")
        print(f"📌 Status: {exp['status']}")
        print("-" * 80)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Query exploration history")
    parser.add_argument("--limit", type=int, default=5, help="Number of recent explorations")

    args = parser.parse_args()
    show_recent_explorations(args.limit)
