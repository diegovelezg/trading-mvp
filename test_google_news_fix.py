#!/usr/bin/env python3
"""Test para verificar que Google News connector convierte FeedParserDict a JSON-serializable"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import json
import logging
from trading_mvp.data_sources.google_news_connector import GoogleNewsConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_news_json_serializable():
    """Test que normalize_data produce JSON-serializable output"""

    print("="*70)
    print("TEST: Google News JSON-serializable")
    print("="*70)

    # 1. Fetch some news
    connector = GoogleNewsConnector()
    print("\n📰 Fetching Google News...")

    raw_news = connector.fetch_data(topic="world", max_items=3)
    print(f"✅ Fetched {len(raw_news)} raw items")

    # 2. Normalize
    print("\n🔧 Normalizing...")
    normalized_news = connector.normalize_data(raw_news)
    print(f"✅ Normalized {len(normalized_news)} items")

    # 3. Test JSON serialization
    print("\n🧪 Testing JSON serialization...")

    all_serializable = True
    for i, item in enumerate(normalized_news):
        try:
            # Intentar serializar a JSON
            json_str = json.dumps(item)
            # Intentar deserializar
            parsed = json.loads(json_str)
            print(f"  ✅ Item {i+1}: JSON-serializable ({len(json_str)} chars)")
        except TypeError as e:
            print(f"  ❌ Item {i+1}: FAILED - {e}")
            all_serializable = False
            # Debug: mostrar qué campos fallan
            for key, value in item.items():
                try:
                    json.dumps(value)
                except TypeError:
                    print(f"     - Field '{key}' has non-serializable type: {type(value)}")

    print("\n" + "="*70)
    if all_serializable:
        print("✅ TEST PASSED: All items are JSON-serializable")
        print("="*70)
        return True
    else:
        print("❌ TEST FAILED: Some items are NOT JSON-serializable")
        print("="*70)
        return False

if __name__ == "__main__":
    success = test_google_news_json_serializable()
    sys.exit(0 if success else 1)
