#!/usr/bin/env python3
"""
Test Decision Agent - Autonomous decision making

Prueba el agente de decisiones en modo MANUAL y AUTOPILOT.

Uso:
    # Modo MANUAL (solo sugerencias)
    python test_decision_agent.py --watchlist-id 3

    # Modo AUTOPILOT (toma decisiones automáticamente)
    AUTOPILOT_MODE=on python test_decision_agent.py --watchlist-id 3
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('test_decision_agent.log'),
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

from run_investment_desk import run_investment_desk, print_investment_desk_report

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test Decision Agent')
    parser.add_argument('--watchlist-id', type=int, default=3, help='Watchlist ID')
    parser.add_argument('--hours-back', type=int, default=48, help='Hours to look back')

    args = parser.parse_args()

    # Check autopilot mode
    autopilot_mode = os.getenv("AUTOPILOT_MODE", "off").lower() == "on"

    print()
    print("="*70)
    print("🤖 DECISION AGENT TEST")
    print("="*70)
    print(f"Mode: {'✈️ AUTOPILOT (Automatic Decisions)' if autopilot_mode else '👨‍💼 MANUAL (Suggestions Only)'}")
    print("="*70)
    print()

    # Run investment desk with decision agent
    result = run_investment_desk(
        watchlist_id=args.watchlist_id,
        hours_back=args.hours_back
    )

    # Print report
    print_investment_desk_report(result)

    # Exit with error code if failed
    if not result.get('success'):
        sys.exit(1)
