import json
import sys
import os
from datetime import datetime

# Setup path and environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from trading_mvp.core.db_manager import get_connection

def default_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def get_latest_analysis(ticker):
    conn = get_connection()
    if not conn:
        print("Failed to connect to DB")
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT ta.recommendation, ta.avg_confidence, ta.positive_ratio, ta.negative_ratio, 
                   ta.top_risks_json, ta.top_opportunities_json, ta.full_results_json, ta.rationale,
                   id.decision, id.action_taken, id.decision_notes
            FROM ticker_analyses ta
            LEFT JOIN investment_decisions id ON ta.id = id.ticker_analysis_id
            WHERE ta.ticker = %s
            ORDER BY ta.analysis_timestamp DESC
            LIMIT 1;
        """, (ticker,))
        
        row = cur.fetchone()
        if row:
            result = {
                'recommendation': row[0],
                'confidence': float(row[1]) if row[1] else 0,
                'positive_ratio': float(row[2]) if row[2] else 0,
                'negative_ratio': float(row[3]) if row[3] else 0,
                'top_risks': row[4] if row[4] else [],
                'top_opportunities': row[5] if row[5] else [],
                'full_results': row[6] if row[6] else {},
                'rationale': row[7],
                'decision': row[8],
                'action_taken': row[9],
                'decision_notes': row[10]
            }
            print(f"\n--- LATEST DATA FOR {ticker} ---")
            print(json.dumps(result, indent=2, default=default_serializer))
        else:
            print(f"\nNo data found for {ticker}")
            
        cur.close()
    finally:
        conn.close()

get_latest_analysis('USO')
get_latest_analysis('PWR')
get_latest_analysis('BWXT')
