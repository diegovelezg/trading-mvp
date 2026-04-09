import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from trading_mvp.core.db_geo_news import insert_geo_news
from trading_mvp.core.db_geo_entities import insert_entities_batch

def main():
    print("📰 Seeding mock GeoMacro news and entities...")
    
    # Mock news 1: Bullish for Energy
    news1 = {
        "title": "Middle East Tensions Drive Crude Oil Prices Higher",
        "summary": "Supply chain concerns in the Middle East have led to a 5% increase in Brent crude prices.",
        "content": "Full article about oil price surge due to geopolitical tensions.",
        "url": "https://example.com/oil-surge",
        "source": "Mock News Service",
        "source_type": "article",
        "published_at": (datetime.now() - timedelta(hours=10)).isoformat(),
        "alpaca_id": 1001,
        "raw_data": {"importance": "high"}
    }
    
    news1_id = insert_geo_news(news1)
    if news1_id:
        print(f"  ✅ Inserted news 1: {news1['title']} (ID: {news1_id})")
        entities1 = [
            {"entity_name": "Crude Oil", "entity_type": "commodity", "impact": "positive", "confidence": 0.9, "sectors": ["Energy"], "regions": ["Middle East"]},
            {"entity_name": "Brent Oil", "entity_type": "commodity", "impact": "positive", "confidence": 0.95, "sectors": ["Energy"], "regions": ["Middle East"]},
            {"entity_name": "Oil & Gas", "entity_type": "sector", "impact": "positive", "confidence": 0.85, "sectors": ["Energy"]}
        ]
        insert_entities_batch(news1_id, entities1, model_used="manual-seed")
    
    # Mock news 2: Bullish for specific companies
    news2 = {
        "title": "Energy Sector Performance Exceeds Expectations",
        "summary": "Major energy companies report strong quarterly earnings amid rising demand.",
        "published_at": (datetime.now() - timedelta(hours=5)).isoformat(),
        "source": "Mock Finance",
        "alpaca_id": 1002
    }
    
    news2_id = insert_geo_news(news2)
    if news2_id:
        print(f"  ✅ Inserted news 2: {news2['title']} (ID: {news2_id})")
        entities2 = [
            {"entity_name": "Energy", "entity_type": "sector", "impact": "positive", "confidence": 0.8, "sectors": ["Energy"]},
            {"entity_name": "ConocoPhillips", "entity_type": "region", "impact": "positive", "confidence": 0.9, "sectors": ["Energy"]}
        ]
        insert_entities_batch(news2_id, entities2, model_used="manual-seed")
        
    print("✅ Mock news seeding complete.")

if __name__ == "__main__":
    main()
