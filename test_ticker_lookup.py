#!/usr/bin/env python3
"""Test ticker→entity→news lookup for USO."""

import sys
import os

# Add paths for import
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.claude', 'subagents'))

from watchlist_manager.agent import get_news_for_ticker, get_ticker_entities

print("="*70)
print("🔍 TESTING TICKER→ENTITY→NEWS LOOKUP")
print("="*70)
print()

# Test USO
ticker = "USO"
print(f"📊 Testing ticker: {ticker}")
print()

# Get entities for USO
entities = get_ticker_entities(ticker)
print(f"🏷️  Entities for {ticker}:")
for entity in entities:
    print(f"   - {entity}")
print()

# Get news via entity matching
news = get_news_for_ticker(ticker, hours_back=24)
print(f"📰 Found {len(news)} news items for {ticker} (via entity matching)")
print()

if news:
    print("Top 5 news items:")
    print()
    for i, item in enumerate(news[:5], 1):
        print(f"{i}. {item.get('title', 'N/A')[:80]}...")
        print(f"   Source: {item.get('source', 'N/A')}")
        print(f"   Published: {item.get('published_at', 'N/A')}")
        print(f"   Summary: {item.get('summary', 'N/A')[:100]}...")
        print()
else:
    print("⚠️  No news found for this ticker")

print("="*70)
