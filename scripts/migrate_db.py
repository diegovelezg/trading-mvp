# Database Migration Script
# Run this to update the explorations table schema

import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from trading_mvp.core.db_manager import get_connection

def migrate_explorations_table():
    """Update the explorations table to include criteria tracking."""

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if table exists and needs migration
        cursor.execute("PRAGMA table_info(explorations)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'criteria' not in columns:
            print("Migrating explorations table...")

            # Create new table with updated schema
            cursor.execute('''
                CREATE TABLE explorations_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    criteria TEXT NOT NULL,
                    tickers TEXT NOT NULL,
                    reasoning TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'discovered'
                )
            ''')

            # Copy existing data
            cursor.execute('''
                INSERT INTO explorations_new (prompt, criteria, tickers, reasoning, timestamp)
                SELECT prompt, '[]' as criteria, results, '' as reasoning, created_at
                FROM explorations
            ''')

            # Drop old table and rename new one
            cursor.execute('DROP TABLE explorations')
            cursor.execute('ALTER TABLE explorations_new RENAME TO explorations')

            conn.commit()
            print("✅ Migration completed successfully")
        else:
            print("✅ Table already has correct schema")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_explorations_table()
