import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from trading_mvp.core.db_manager import get_connection

def migrate():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if alpaca_order_id exists
        cursor.execute("PRAGMA table_info(investment_decisions)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'alpaca_order_id' not in columns:
            print("Adding alpaca_order_id to investment_decisions...")
            cursor.execute("ALTER TABLE investment_decisions ADD COLUMN alpaca_order_id TEXT")
            conn.commit()
            print("✅ Migration completed successfully")
        else:
            print("✅ Column already exists")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
