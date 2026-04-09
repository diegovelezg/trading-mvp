import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from trading_mvp.core.db_geo_news import insert_geo_news
from trading_mvp.core.db_geo_entities import insert_entities_batch

def main():
    print("📰 Seeding COMPLEX GeoMacro news (Bull + Bear evidence)...")
    
    # News 3: Bearish Risks for Energy (to populate Bear Risks)
    news3 = {
        "title": "Global Demand Concerns as Industrial Production Slows",
        "summary": "Economic data from major importers suggests a potential slowdown in energy consumption.",
        "content": "Detailed report on recession risks and their impact on oil demand forecasts.",
        "url": "https://example.com/demand-risks",
        "source": "Global Economic Watch",
        "source_type": "report",
        "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "alpaca_id": 1003
    }
    
    news3_id = insert_geo_news(news3)
    if news3_id:
        print(f"  ✅ Inserted news 3: {news3['title']} (ID: {news3_id})")
        entities3 = [
            {"entity_name": "Recession Fears", "entity_type": "theme", "impact": "negative", "confidence": 0.8, "sectors": ["Energy", "Industrial"]},
            {"entity_name": "Demand Destruction", "entity_type": "theme", "impact": "negative", "confidence": 0.85, "sectors": ["Energy"]},
            {"entity_name": "OPEC+ Overproduction", "entity_type": "policy", "impact": "negative", "confidence": 0.7, "sectors": ["Energy"]}
        ]
        insert_entities_batch(news3_id, entities3, model_used="manual-seed")
        
    print("✅ Complex news seeding complete.")

if __name__ == "__main__":
    main()
