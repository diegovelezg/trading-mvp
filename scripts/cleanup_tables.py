import os
import sys
from dotenv import load_dotenv
import psycopg2

# Cargar variables de entorno
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def cleanup_and_verify():
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found")
        return

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    
    try:
        with conn.cursor() as cur:
            print("--- CLEANING UP LEGACY TABLES ---")
            legacy_tables = ['investment_runs', 'ticker_analysis']
            for table in legacy_tables:
                cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                print(f"✅ Dropped legacy table: {table}")
            
            print("\n--- VERIFYING PLURAL SCHEMA ---")
            plural_tables = [
                'investment_desk_runs', 
                'ticker_analyses', 
                'investment_decisions', 
                'recommendation_performance'
            ]
            for table in plural_tables:
                cur.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                exists = cur.fetchone()[0]
                if exists:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    print(f"✅ {table:<30} | EXISTS ({count} rows)")
                else:
                    print(f"❌ {table:<30} | MISSING")
                    
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_and_verify()
