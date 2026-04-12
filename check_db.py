import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from trading_mvp.core.db_manager import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute("""
    SELECT d.ticker, d.decision_timestamp, d.recommendation, d.decision, d.action_taken, d.decision_notes 
    FROM investment_decisions d
    ORDER BY d.decision_timestamp DESC
    LIMIT 5;
""")
rows = cur.fetchall()
print(f"{'TICKER':<10} | {'TIMESTAMP':<25} | {'REC':<10} | {'DECISION':<10} | {'ACTION':<10} | {'NOTES'}")
print("-" * 120)
for r in rows:
    print(f"{r[0]:<10} | {str(r[1]):<25} | {r[2]:<10} | {r[3]:<10} | {r[4]:<10} | {r[5]}")
cur.close()
conn.close()
