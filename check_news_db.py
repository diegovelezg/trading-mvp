import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from trading_mvp.core.db_manager import get_connection

def check_news():
    conn = get_connection()
    if not conn:
        print("Failed to connect to DB")
        return
        
    try:
        cur = conn.cursor()
        
        # Check total news count
        cur.execute("SELECT COUNT(*) FROM news_embeddings;")
        total_news = cur.fetchone()[0]
        print(f"Total news in DB: {total_news}")
        
        # Check news in the last few days (April 24 - April 27)
        cur.execute("""
            SELECT ticker, COUNT(*) as news_count, MIN(published_at) as oldest, MAX(published_at) as newest
            FROM news_embeddings 
            WHERE published_at >= '2026-04-20' AND published_at <= '2026-04-28'
            GROUP BY ticker
            ORDER BY news_count DESC
            LIMIT 20;
        """)
        
        recent_news = cur.fetchall()
        print("\nRecent news counts by ticker (April 20 - April 28):")
        for r in recent_news:
            print(f"Ticker: {r[0]:<5} | Count: {r[1]:<4} | Oldest: {r[2]} | Newest: {r[3]}")
            
        # specifically check one of the tickers that failed, e.g., 'GWW' or 'PH'
        cur.execute("""
            SELECT id, title, published_at 
            FROM news_embeddings 
            WHERE ticker IN ('GWW', 'PH', 'BKR', 'SNPS', 'IEX')
            ORDER BY published_at DESC
            LIMIT 5;
        """)
        
        specific_news = cur.fetchall()
        print("\nSpecific news for GWW, PH, BKR, SNPS, IEX:")
        for r in specific_news:
            print(f"ID: {r[0]} | Date: {r[2]} | Title: {r[1][:50]}...")
            
        cur.close()
    finally:
        conn.close()

if __name__ == "__main__":
    check_news()