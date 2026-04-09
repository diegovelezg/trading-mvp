import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from trading_mvp.core.db_watchlist import create_watchlist, add_ticker_to_watchlist

def main():
    print("🌱 Seeding initial demo data...")
    
    # 1. Create a watchlist
    name = "Energy Market Leaders"
    description = "Leading energy ETFs and oil exploration companies for sectoral analysis."
    criteria_prompt = "Identify leading energy ETFs and oil exploration companies."
    
    watchlist_id = create_watchlist(
        name=name,
        description=description,
        criteria_prompt=criteria_prompt,
        criteria_summary="Focus on broad energy (XLE), oil exploration (XOP), Brent oil (BNO), and major energy producers (COP, CVE)."
    )
    
    if watchlist_id:
        print(f"✅ Created watchlist '{name}' with ID {watchlist_id}")
        
        # 2. Add tickers
        tickers_to_add = [
            {"ticker": "XLE", "company_name": "Energy Select Sector SPDR Fund", "reason": "Broad energy sector ETF"},
            {"ticker": "XOP", "company_name": "SPDR S&P Oil & Gas Exploration & Production ETF", "reason": "Oil & gas exploration companies"},
            {"ticker": "BNO", "company_name": "United States Brent Oil Fund", "reason": "Brent crude oil ETF"},
            {"ticker": "CVE", "company_name": "Cenovus Energy", "reason": "Canadian integrated oil company"},
            {"ticker": "COP", "company_name": "ConocoPhillips", "reason": "American multinational energy company"},
        ]
        
        added_count = 0
        for ticker_data in tickers_to_add:
            if add_ticker_to_watchlist(
                watchlist_id=watchlist_id,
                ticker=ticker_data['ticker'],
                company_name=ticker_data['company_name'],
                reason=ticker_data['reason']
            ):
                print(f"  ✅ Added {ticker_data['ticker']}")
                added_count += 1
                
        print(f"📊 Successfully seeded {added_count} tickers.")
    else:
        print("❌ Failed to create watchlist.")

if __name__ == "__main__":
    main()
