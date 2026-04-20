import json
from trading_mvp.core.db_geo_news import get_connection
from psycopg2.extras import RealDictCursor

def get_last_run_decisions():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get last run ID
            cur.execute("SELECT id, run_timestamp, overall_sentiment FROM investment_desk_runs ORDER BY run_timestamp DESC LIMIT 1")
            last_run = cur.fetchone()
            if not last_run:
                print("No runs found.")
                return

            print(f"--- RUN {last_run['id']} ({last_run['run_timestamp']}) - Sentiment: {last_run['overall_sentiment']} ---")

            # Get decisions for this run
            cur.execute("""
                SELECT 
                    d.ticker, 
                    d.desk_action, 
                    d.decision_notes as decision_rationale,
                    ta.recommendation as agent_recommendation,
                    ta.avg_confidence as nlp_confidence,
                    ta.rationale as analysis_rationale
                FROM investment_decisions d
                LEFT JOIN ticker_analyses ta ON d.ticker_analysis_id = ta.id
                WHERE d.desk_run_id = %s
                ORDER BY d.ticker
            """, (last_run['id'],))
            
            decisions = cur.fetchall()
            for d in decisions:
                print(f"\n[{d['ticker']}] - Action: {d['desk_action']}")
                print(f"NLP Rec: {d['agent_recommendation']} (Conf: {d['nlp_confidence']:.2f})")
                print(f"Analysis Rationale: {d['analysis_rationale']}")
                print(f"Decision Rationale: {d['decision_rationale']}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    get_last_run_decisions()
