#!/usr/bin/env python3
"""Test para verificar que TODOS los conectores producen JSON-serializable output"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import json
import logging
from trading_mvp.data_sources import AlpacaNewsConnector, GoogleNewsConnector, SerpApiConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connector(name, connector, fetch_method):
    """Test a connector's JSON serialization"""
    print(f"\n{'='*70}")
    print(f"TEST: {name} - JSON-serializable")
    print('='*70)

    # Fetch
    print(f"📰 Fetching from {name}...")
    raw = fetch_method()
    print(f"✅ Fetched {len(raw)} raw items")

    # Normalize
    print(f"🔧 Normalizing...")
    normalized = connector.normalize_data(raw)
    print(f"✅ Normalized {len(normalized)} items")

    # Test JSON serialization
    print(f"🧪 Testing JSON serialization...")
    all_ok = True
    for i, item in enumerate(normalized):
        try:
            json_str = json.dumps(item)
            parsed = json.loads(json_str)
        except TypeError as e:
            print(f"  ❌ Item {i+1}: FAILED - {e}")
            all_ok = False
            # Debug
            for key, value in item.items():
                try:
                    json.dumps(value)
                except TypeError:
                    print(f"     - Field '{key}' has non-serializable type: {type(value)}")

    if all_ok:
        print(f"  ✅ All {len(normalized)} items are JSON-serializable")
        print('='*70)
        return True
    else:
        print(f"  ❌ Some items FAILED")
        print('='*70)
        return False

def main():
    """Test all connectors"""
    print("\n" + "="*70)
    print("TESTING ALL NEWS CONNECTORS - JSON SERIALIZABILITY")
    print("="*70)

    results = {}

    # Test Alpaca (limit to 2 items)
    try:
        alpaca = AlpacaNewsConnector()
        results['alpaca'] = test_connector(
            "Alpaca",
            alpaca,
            lambda: alpaca.fetch_macro_news(hours_back=24)[:2]
        )
    except Exception as e:
        print(f"❌ Alpaca FAILED: {e}")
        results['alpaca'] = False

    # Test Google (limit to 2 items)
    try:
        google = GoogleNewsConnector()
        results['google'] = test_connector(
            "Google News",
            google,
            lambda: google.fetch_data(topic="world", max_items=2)
        )
    except Exception as e:
        print(f"❌ Google FAILED: {e}")
        results['google'] = False

    # Test SERPAPI (limit to 2 items)
    try:
        serpapi = SerpApiConnector()
        results['serpapi'] = test_connector(
            "SERPAPI",
            serpapi,
            lambda: serpapi.fetch_data(query="news", max_items=2)
        )
    except Exception as e:
        print(f"❌ SERPAPI FAILED: {e}")
        results['serpapi'] = False

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name}: {status}")

    all_passed = all(results.values())
    print("="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*70)

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
