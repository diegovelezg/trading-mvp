import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from trading_mvp.core.db_manager import get_connection

def default_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def fetch_latest_run_data():
    conn = get_connection()
    if not conn:
        print("Failed to connect to DB")
        return
    try:
        cur = conn.cursor()
        
        # Get the latest run
        cur.execute("SELECT id, run_timestamp, total_tickers, desk_outlook FROM investment_desk_runs ORDER BY run_timestamp DESC LIMIT 1;")
        run_row = cur.fetchone()
        if not run_row:
            print("No runs found.")
            return
            
        run_id = run_row[0]
        
        # Get all decisions and analyses for this run
        cur.execute("""
            SELECT 
                d.ticker, 
                d.recommendation as desk_rec, 
                d.decision, 
                d.action_taken, 
                d.decision_notes,
                a.avg_confidence, 
                a.positive_ratio, 
                a.negative_ratio,
                a.full_results_json, 
                a.rationale,
                a.top_risks_json,
                a.top_opportunities_json
            FROM investment_decisions d
            JOIN ticker_analyses a ON d.ticker_analysis_id = a.id
            WHERE d.desk_run_id = %s
            ORDER BY d.ticker;
        """, (run_id,))
        
        rows = cur.fetchall()
        
        results = []
        for r in rows:
            results.append({
                "ticker": r[0],
                "recommendation": r[1],
                "decision": r[2],
                "action_taken": r[3],
                "decision_notes": r[4],
                "avg_confidence": float(r[5]) if r[5] else None,
                "positive_ratio": float(r[6]) if r[6] else None,
                "negative_ratio": float(r[7]) if r[7] else None,
                "full_results": json.loads(r[8]) if r[8] and isinstance(r[8], str) else r[8],
                "rationale": r[9],
                "top_risks": json.loads(r[10]) if r[10] and isinstance(r[10], str) else r[10],
                "top_opportunities": json.loads(r[11]) if r[11] and isinstance(r[11], str) else r[11]
            })
            
        print(json.dumps({
            "run_id": run_id,
            "run_timestamp": run_row[1],
            "total_tickers": run_row[2],
            "desk_outlook": run_row[3],
            "decisions": results
        }, indent=2, default=default_serializer))
        
        cur.close()
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_latest_run_data()
