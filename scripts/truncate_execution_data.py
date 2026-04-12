import os
import sys
from dotenv import load_dotenv
import psycopg2

# Cargar variables de entorno
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def truncate_execution_data():
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        
        with conn.cursor() as cur:
            print("🧹 Truncating execution data tables...")
            
            # Truncate plural tables with CASCADE to handle foreign key dependencies
            tables = [
                'investment_desk_runs', 
                'ticker_analyses', 
                'investment_decisions', 
                'recommendation_performance'
            ]
            
            for table in tables:
                # Check if table exists first
                cur.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                if cur.fetchone()[0]:
                    cur.execute(f"TRUNCATE TABLE {table} CASCADE")
                    print(f"   ✅ Truncated: {table}")
                else:
                    print(f"   ⚠️  Skipped (not found): {table}")
            
            print("\n✨ Database feed cleared successfully.")
                    
    except Exception as e:
        print(f"❌ Error during truncation: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    truncate_execution_data()
