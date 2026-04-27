import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from trading_mvp.core.db_geo_news import get_recent_news
from trading_mvp.core.semantic_news_search import find_related_news_for_ticker
from trading_mvp.core.dna_manager import DNAManager

def test_news_search(ticker):
    print(f"\n--- Testing news search for {ticker} ---")
    
    # 1. Check DNA
    dna_manager = DNAManager()
    dna = dna_manager.get_dna(ticker)
    if not dna:
        print(f"Failed to load DNA for {ticker}")
        return
    print(f"DNA loaded. Asset type: {dna.get('asset_type')}")
    
    # 2. Get recent news
    # For testing, let's use a very large hours_back to ensure we capture news from April 24-27
    # Today's date is April 27, 2026. Let's say 120 hours back (5 days)
    hours_back = 120
    all_news = get_recent_news(hours_back=hours_back)
    print(f"Found {len(all_news)} total recent news items (last {hours_back}h).")
    
    if not all_news:
        print("No news found in DB at all!")
        return
        
    # Print the oldest and newest dates of the retrieved news
    dates = [n.get('published_at') for n in all_news if n.get('published_at')]
    if dates:
        print(f"Oldest news in batch: {min(dates)}")
        print(f"Newest news in batch: {max(dates)}")
    
    # 3. Search semantic
    related_news, search_stats = find_related_news_for_ticker(
        ticker,
        all_news,
        method='semantic',
        similarity_threshold=0.75,
        hours_back=hours_back
    )
    
    print(f"Found {len(related_news)} related news for {ticker}.")
    if search_stats:
        print(f"Search stats: {search_stats}")
        
    for i, n in enumerate(related_news[:3]):
        print(f"[{i+1}] {n.get('title')[:80]}... (Score: {n.get('similarity_score')})")

if __name__ == "__main__":
    test_news_search("BKR")
    test_news_search("PH")
    test_news_search("GWW")
    test_news_search("AAPL")
