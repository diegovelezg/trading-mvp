import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from trading_mvp.core.db_manager import init_db
from trading_mvp.core.db_watchlist import create_watchlist_tables
from trading_mvp.core.db_investment_tracking import create_investment_tracking_tables
from trading_mvp.core.db_geo_news import create_geo_macro_news_table
from trading_mvp.core.db_geo_entities import create_geo_macro_entities_table

def main():
    print("Initializing core database tables...")
    init_db()
    
    print("Initializing watchlist tables...")
    create_watchlist_tables()
    
    print("Initializing investment tracking tables...")
    create_investment_tracking_tables()

    print("Initializing GeoMacro news tables...")
    create_geo_macro_news_table()

    print("Initializing GeoMacro entities tables...")
    create_geo_macro_entities_table()
    
    print("✅ All database tables initialized successfully.")

if __name__ == "__main__":
    main()
