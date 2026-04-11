import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Cargar variables de entorno
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL env var missing")
    sys.exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        print(f"{'Table Name':<30} | {'Count':<10}")
        print("-" * 45)
        
        for table in tables:
            name = table['table_name']
            try:
                cur.execute(f"SELECT COUNT(*) FROM {name}")
                count = cur.fetchone()['count']
                print(f"{name:<30} | {count:<10}")
            except Exception as e:
                print(f"{name:<30} | ERROR: {str(e)[:40]}")
                conn.rollback() # Important to rollback after error to continue
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
