#!/usr/bin/env python3
"""Add multiple tickers to watchlist for testing investment desk."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trading_mvp.core.dashboard_api_client import add_ticker_to_watchlist, get_active_watchlists

# Obtener watchlist activa (usar la primera disponible)
watchlists = get_active_watchlists()
if not watchlists:
    print("❌ No hay watchlists activas. Crea una primero.")
    sys.exit(1)

watchlist_id = watchlists[0]['id']
print(f"📋 Usando watchlist ID={watchlist_id}: {watchlists[0]['name']}")

# Add energy-related tickers
tickers_to_add = [
    {"ticker": "XLE", "company_name": "Energy Select Sector SPDR Fund", "reason": "Broad energy sector ETF"},
    {"ticker": "XOP", "company_name": "SPDR S&P Oil & Gas Exploration & Production ETF", "reason": "Oil & gas exploration companies"},
    {"ticker": "BNO", "company_name": "United States Brent Oil Fund", "reason": "Brent crude oil ETF"},
    {"ticker": "CVE", "company_name": "Cenovus Energy", "reason": "Canadian integrated oil company"},
    {"ticker": "COP", "company_name": "ConocoPhillips", "reason": "American multinational energy company"},
]

print(f"📋 Adding {len(tickers_to_add)} tickers to watchlist {watchlist_id}...")

added_count = 0
for ticker_data in tickers_to_add:
    ticker = ticker_data['ticker']
    company_name = ticker_data['company_name']
    reason = ticker_data['reason']

    try:
        ticker_id = add_ticker_to_watchlist(
            watchlist_id=watchlist_id,
            ticker=ticker,
            company_name=company_name,
            reason=reason
        )

        if ticker_id:
            print(f"  ✅ Added {ticker}: {company_name}")
            added_count += 1
        else:
            print(f"  ⚠️  {ticker} already exists or failed")

    except Exception as e:
        print(f"  ❌ Failed to add {ticker}: {e}")

print(f"\n📊 Successfully added {added_count}/{len(tickers_to_add)} tickers")

# Verify (via Dashboard API)
watchlists = get_active_watchlists()
watchlist = next((wl for wl in watchlists if wl['id'] == watchlist_id), None)

if watchlist:
    tickers = watchlist.get('items', [])
    print(f"\n📋 Watchlist now has {len(tickers)} tickers:")
    for t in tickers:
        print(f"  • {t['ticker']}: {t.get('company_name', 'N/A')}")
else:
    print(f"\n⚠️  Could not verify watchlist {watchlist_id}")
