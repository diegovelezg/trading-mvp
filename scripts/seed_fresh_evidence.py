import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from trading_mvp.core.db_geo_news import insert_geo_news
from trading_mvp.core.db_geo_entities import insert_entities_batch

def main():
    print("📰 Seeding FRESH mixed news evidence...")
    
    # 1. Bullish News
    news1 = {
        "title": "Middle East Tensions Drive Crude Oil Prices Higher",
        "summary": "Supply chain concerns in the Middle East have led to a 5% increase in Brent crude prices.",
        "published_at": (datetime.now() - timedelta(hours=10)).isoformat(),
        "source": "Energy Daily",
        "alpaca_id": 2001
    }
    nid1 = insert_geo_news(news1)
    if nid1:
        insert_entities_batch(nid1, [
            {"entity_name": "Crude Oil", "entity_type": "commodity", "impact": "positive", "confidence": 0.9, "sectors": ["Energy"]},
            {"entity_name": "Brent Oil", "entity_type": "commodity", "impact": "positive", "confidence": 0.95, "sectors": ["Energy"]}
        ], model_used="fresh-seed")

    # 2. Bearish News
    news2 = {
        "title": "Global Demand Concerns as Industrial Production Slows",
        "summary": "Economic data suggests potential slowdown in energy consumption.",
        "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "source": "Macro Economics",
        "alpaca_id": 2002
    }
    nid2 = insert_geo_news(news2)
    if nid2:
        insert_entities_batch(nid2, [
            {"entity_name": "Recession Fears", "entity_type": "theme", "impact": "negative", "confidence": 0.8, "sectors": ["Energy"]},
            {"entity_name": "Demand Destruction", "entity_type": "theme", "impact": "negative", "confidence": 0.85, "sectors": ["Energy"]}
        ], model_used="fresh-seed")
        
    print("✅ Fresh evidence seeding complete.")

if __name__ == "__main__":
    main()
