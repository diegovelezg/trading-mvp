"""Database schema for investment decisions tracking (audit trail)."""

import logging
import json
from typing import List, Dict, Optional
from datetime import datetime
from trading_mvp.core.db_manager import get_connection
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


def create_investment_tracking_tables():
    """Create all investment tracking tables."""

    conn = get_connection()
    with conn.cursor() as cur:
        # 1. Desk runs (complete investment desk analysis)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS investment_desk_runs (
                id SERIAL PRIMARY KEY,

                -- Run metadata
                run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                watchlist_id INTEGER NOT NULL,
                watchlist_name VARCHAR(255),

                -- Analysis parameters
                time_window_hours INTEGER,
                duration_seconds FLOAT,

                -- Overall desk results
                overall_sentiment VARCHAR(50),  -- BULLISH, BEARISH, CAUTIOUSLY_BULLISH, etc.
                desk_outlook TEXT,

                -- Aggregate metrics
                total_tickers INTEGER,
                analyzed_tickers INTEGER,
                failed_tickers TEXT,  -- JSON array
                total_news_analyzed INTEGER,
                total_entities_found INTEGER,

                avg_confidence FLOAT,
                avg_negative_ratio FLOAT,
                avg_positive_ratio FLOAT,

                -- Recommendation breakdown
                bullish_count INTEGER,
                bearish_count INTEGER,
                cautious_count INTEGER,
                neutral_count INTEGER,

                -- Full results (JSON)
                full_results_json TEXT,

                -- Desk recommendations (JSON)
                recommendations_json TEXT
            );
        """)

        # 2. Individual ticker analyses
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ticker_analyses (
                id SERIAL PRIMARY KEY,

                -- Link to desk run
                desk_run_id INTEGER,

                -- Ticker info
                ticker VARCHAR(10) NOT NULL,
                company_name VARCHAR(255),

                -- Analysis timestamp
                analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                -- Entity mapping
                mapped_entities TEXT,  -- JSON array

                -- News summary
                related_news_count INTEGER,
                news_sources TEXT,  -- JSON array
                news_ids TEXT,  -- JSON array of news IDs used

                -- Entity analysis
                unique_entities_found INTEGER,
                total_entity_mentions INTEGER,

                -- Sentiment scores
                avg_confidence FLOAT,
                negative_ratio FLOAT,
                positive_ratio FLOAT,

                -- Recommendation
                recommendation VARCHAR(50),  -- BULLISH, BEARISH, CAUTIOUS, NEUTRAL
                rationale TEXT,

                -- Top insights (JSON)
                top_risks_json TEXT,
                top_opportunities_json TEXT,
                most_mentioned_json TEXT,

                -- Full results (JSON)
                full_results_json TEXT,

                FOREIGN KEY (desk_run_id) REFERENCES investment_desk_runs(id) ON DELETE CASCADE
            );
        """)

        # 3. Decision tracking (what was done with the recommendation)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS investment_decisions (
                id SERIAL PRIMARY KEY,

                -- Link to analysis
                ticker_analysis_id INTEGER NOT NULL,
                desk_run_id INTEGER NOT NULL,
                ticker VARCHAR(10) NOT NULL,

                -- Alpaca link
                alpaca_order_id TEXT,

                -- The recommendation
                recommendation VARCHAR(50),  -- BULLISH, BEARISH, CAUTIOUS, NEUTRAL
                desk_action VARCHAR(50),  -- BUY, AVOID, WATCH, HOLD

                -- Decision made by user
                decision VARCHAR(50),  -- FOLLOWED, IGNORED, MODIFIED
                decision_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                decision_notes TEXT,

                -- Execution
                action_taken VARCHAR(100),  -- BOUGHT, SOLD, HELD, HEDGED, NONE
                execution_timestamp TIMESTAMP,

                -- Position details (if executed)
                position_size FLOAT,
                entry_price FLOAT,
                target_price FLOAT,
                stop_loss FLOAT,

                -- Outcome
                exit_price FLOAT,
                exit_timestamp TIMESTAMP,
                profit_loss FLOAT,
                profit_loss_pct FLOAT,

                -- Status
                status VARCHAR(50) DEFAULT 'PENDING',  -- PENDING, OPEN, CLOSED, CANCELLED

                FOREIGN KEY (ticker_analysis_id) REFERENCES ticker_analyses(id),
                FOREIGN KEY (desk_run_id) REFERENCES investment_desk_runs(id)
            );
        """)

        # 4. Performance tracking
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recommendation_performance (
                id SERIAL PRIMARY KEY,

                -- Link to decision
                decision_id INTEGER NOT NULL,

                -- Was the recommendation correct?
                was_correct BOOLEAN,
                actual_outcome VARCHAR(50),  -- PROFIT, LOSS, BREAKEVEN

                -- Time to outcome
                days_to_outcome INTEGER,

                -- Market context at outcome
                outcome_notes TEXT,

                -- Lessons learned
                lessons_learned TEXT,

                -- Rating (1-5 stars)
                rating INTEGER,

                outcome_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (decision_id) REFERENCES investment_decisions(id)
            );
        """)

        # Indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_desk_runs_watchlist
            ON investment_desk_runs(run_timestamp DESC);
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_ticker_analyses_ticker
            ON ticker_analyses(ticker, analysis_timestamp DESC);
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_decisions_ticker
            ON investment_decisions(ticker, decision_timestamp DESC);
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_decisions_status
            ON investment_decisions(status);
        """)

    conn.commit()
    conn.close()

    logger.info("✅ Investment tracking tables created")


def save_desk_run(desk_analysis: Dict) -> Optional[int]:
    """Save a complete investment desk run.

    Args:
        desk_analysis: Full desk analysis from run_investment_desk()

    Returns:
        desk_run_id, or None if failed
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            watchlist = desk_analysis['watchlist']

            cur.execute("""
                INSERT INTO investment_desk_runs
                (watchlist_id, watchlist_name, time_window_hours, duration_seconds,
                 overall_sentiment, desk_outlook,
                 total_tickers, analyzed_tickers, failed_tickers,
                 total_news_analyzed, total_entities_found,
                 avg_confidence, avg_negative_ratio, avg_positive_ratio,
                 bullish_count, bearish_count, cautious_count, neutral_count,
                 full_results_json, recommendations_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                watchlist['id'],
                watchlist['name'],
                desk_analysis['time_window_hours'],
                desk_analysis['duration_seconds'],
                desk_analysis['overall_sentiment'],
                desk_analysis['desk_outlook'],
                desk_analysis['total_tickers'],
                desk_analysis['analyzed_tickers'],
                json.dumps(desk_analysis['failed_tickers']),
                desk_analysis['total_news_analyzed'],
                desk_analysis['total_entities_found'],
                desk_analysis['avg_confidence'],
                desk_analysis['avg_negative_ratio'],
                desk_analysis['avg_positive_ratio'],
                desk_analysis['bullish_count'],
                desk_analysis['bearish_count'],
                desk_analysis['cautious_count'],
                desk_analysis['neutral_count'],
                json.dumps(desk_analysis),
                json.dumps(desk_analysis['recommendations'])
            ))

            desk_run_id = cur.fetchone()[0]
            conn.commit()
            logger.info(f"✅ Saved desk run {desk_run_id}")
            return desk_run_id

    except Exception as e:
        logger.error(f"❌ Failed to save desk run: {e}")
        return None
    finally:
        conn.close()


def save_ticker_analysis(ticker_analysis: Dict, desk_run_id: int) -> Optional[int]:
    """Save an individual ticker analysis.

    Args:
        ticker_analysis: Full ticker analysis from analyze_ticker()
        desk_run_id: Parent desk run ID

    Returns:
        ticker_analysis_id, or None if failed
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO ticker_analyses
                (desk_run_id, ticker, company_name, analysis_timestamp,
                 mapped_entities, related_news_count, news_sources, news_ids,
                 unique_entities_found, total_entity_mentions,
                 avg_confidence, negative_ratio, positive_ratio,
                 recommendation, rationale,
                 top_risks_json, top_opportunities_json, most_mentioned_json,
                 full_results_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                desk_run_id,
                ticker_analysis['ticker'],
                ticker_analysis.get('company_name'),  # Optional
                ticker_analysis['analysis_timestamp'],
                json.dumps(ticker_analysis['mapped_entities']),
                ticker_analysis['related_news_count'],
                json.dumps(ticker_analysis['news_sources']),
                json.dumps([n.get('id') for n in ticker_analysis.get('related_news', [])]),
                ticker_analysis['unique_entities_found'],
                ticker_analysis['unique_entities_found'],  # Using same value for now
                ticker_analysis['avg_confidence'],
                ticker_analysis['negative_ratio'],
                ticker_analysis['positive_ratio'],
                ticker_analysis['recommendation'],
                ticker_analysis['rationale'],
                json.dumps(ticker_analysis.get('top_risks', [])),
                json.dumps(ticker_analysis.get('top_opportunities', [])),
                json.dumps(ticker_analysis.get('most_mentioned', [])),
                json.dumps(ticker_analysis)
            ))

            ticker_analysis_id = cur.fetchone()[0]
            conn.commit()
            logger.info(f"✅ Saved ticker analysis {ticker_analysis_id} for {ticker_analysis['ticker']}")
            return ticker_analysis_id

    except Exception as e:
        logger.error(f"❌ Failed to save ticker analysis: {e}")
        return None
    finally:
        conn.close()


def record_decision(
    ticker_analysis_id: int,
    desk_run_id: int,
    ticker: str,
    recommendation: str,
    desk_action: str,
    decision: str,
    decision_notes: str = None,
    action_taken: str = None,
    position_size: float = None,
    entry_price: float = None,
    alpaca_order_id: str = None
) -> Optional[int]:
    """Record an investment decision based on analysis.

    Args:
        ticker_analysis_id: Ticker analysis ID
        desk_run_id: Desk run ID
        ticker: Ticker symbol
        recommendation: Original recommendation (BULLISH/BEARISH/CAUTIOUS)
        desk_action: Desk action (BUY/AVOID/WATCH)
        decision: What user decided (FOLLOWED/IGNORED/MODIFIED)
        decision_notes: Notes explaining the decision
        action_taken: What action was taken (BOUGHT/SOLD/HELD/HEDGED/NONE)
        position_size: Size of position (if executed)
        entry_price: Entry price (if executed)
        alpaca_order_id: Alpaca order ID (if executed)

    Returns:
        decision_id, or None if failed
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO investment_decisions
                (ticker_analysis_id, desk_run_id, ticker, recommendation, desk_action,
                 decision, decision_notes, action_taken, position_size, entry_price, alpaca_order_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                ticker_analysis_id,
                desk_run_id,
                ticker,
                recommendation,
                desk_action,
                decision,
                decision_notes,
                action_taken,
                position_size,
                entry_price,
                alpaca_order_id
            ))

            decision_id = cur.fetchone()[0]
            conn.commit()
            logger.info(f"✅ Recorded decision {decision_id} for {ticker}: {decision}")
            return decision_id

    except Exception as e:
        logger.error(f"❌ Failed to record decision: {e}")
        return None
    finally:
        conn.close()


def update_decision_outcome(
    decision_id: int,
    exit_price: float,
    profit_loss: float,
    profit_loss_pct: float,
    status: str = 'CLOSED',
    was_correct: bool = None,
    actual_outcome: str = None,
    outcome_notes: str = None,
    rating: int = None
) -> bool:
    """Update a decision with its outcome.

    Args:
        decision_id: Decision ID
        exit_price: Exit price
        profit_loss: Absolute profit/loss
        profit_loss_pct: Percentage profit/loss
        status: New status (CLOSED, etc)
        was_correct: Was the original recommendation correct?
        actual_outcome: PROFIT, LOSS, BREAKEVEN
        outcome_notes: Notes on outcome
        rating: 1-5 star rating

    Returns:
        True if successful
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Update decision
            cur.execute("""
                UPDATE investment_decisions
                SET exit_price = %s,
                    exit_timestamp = CURRENT_TIMESTAMP,
                    profit_loss = %s,
                    profit_loss_pct = %s,
                    status = %s
                WHERE id = %s
            """, (exit_price, profit_loss, profit_loss_pct, status, decision_id))

            # Add performance record
            if any([was_correct is not None, actual_outcome, outcome_notes, rating]):
                cur.execute("""
                    INSERT INTO recommendation_performance
                    (decision_id, was_correct, actual_outcome, outcome_notes, rating)
                    VALUES (%s, %s, %s, %s, %s)
                """, (decision_id, was_correct, actual_outcome, outcome_notes, rating))

            conn.commit()
            logger.info(f"✅ Updated outcome for decision {decision_id}")
            return True

    except Exception as e:
        logger.error(f"❌ Failed to update outcome: {e}")
        return False
    finally:
        conn.close()


def get_decision_history(ticker: str = None, limit: int = 50) -> List[Dict]:
    """Get decision history with full context.

    Args:
        ticker: Filter by ticker (optional)
        limit: Max records to return

    Returns:
        List of decision records with full context
    """

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if ticker:
                cur.execute("""
                    SELECT
                        d.*,
                        t.recommendation as ticker_recommendation,
                        t.rationale as ticker_rationale,
                        t.avg_confidence,
                        dr.overall_sentiment as desk_sentiment,
                        dr.watchlist_name
                    FROM investment_decisions d
                    JOIN ticker_analyses t ON d.ticker_analysis_id = t.id
                    JOIN investment_desk_runs dr ON d.desk_run_id = dr.id
                    WHERE d.ticker = %s
                    ORDER BY d.decision_timestamp DESC
                    LIMIT %s
                """, (ticker, limit))
            else:
                cur.execute("""
                    SELECT
                        d.*,
                        t.recommendation as ticker_recommendation,
                        t.rationale as ticker_rationale,
                        t.avg_confidence,
                        dr.overall_sentiment as desk_sentiment,
                        dr.watchlist_name
                    FROM investment_decisions d
                    JOIN ticker_analyses t ON d.ticker_analysis_id = t.id
                    JOIN investment_desk_runs dr ON d.desk_run_id = dr.id
                    ORDER BY d.decision_timestamp DESC
                    LIMIT %s
                """, (limit,))

            rows = cur.fetchall()
            return [dict(row) for row in rows]
    finally:
        conn.close()


def get_performance_stats(ticker: str = None) -> Dict:
    """Get performance statistics.

    Args:
        ticker: Filter by ticker (optional)

    Returns:
        Performance statistics
    """

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if ticker:
                where_clause = "WHERE d.ticker = %s"
                params = (ticker,)
            else:
                where_clause = ""
                params = ()

            cur.execute(f"""
                SELECT
                    COUNT(*) as total_decisions,
                    COUNT(CASE WHEN d.status = 'CLOSED' THEN 1 END) as closed_decisions,
                    COUNT(CASE WHEN d.action_taken = 'BOUGHT' THEN 1 END) as bought_count,
                    SUM(CASE WHEN d.profit_loss IS NOT NULL THEN d.profit_loss ELSE 0 END) as total_pl,
                    AVG(CASE WHEN d.profit_loss_pct IS NOT NULL THEN d.profit_loss_pct ELSE NULL END) as avg_pl_pct,
                    COUNT(CASE WHEN p.was_correct = true THEN 1 END) as correct_recommendations,
                    COUNT(CASE WHEN p.was_correct = false THEN 1 END) as incorrect_recommendations,
                    AVG(CASE WHEN p.rating IS NOT NULL THEN p.rating ELSE NULL END) as avg_rating
                FROM investment_decisions d
                LEFT JOIN recommendation_performance p ON d.id = p.decision_id
                {where_clause}
            """, params)

            row = cur.fetchone()
            return dict(row) if row else {}
    finally:
        conn.close()


def get_audit_trail(ticker: str, hours_back: int = 48) -> List[Dict]:
    """Get full audit trail for a ticker.

    Args:
        ticker: Ticker symbol
        hours_back: Hours to look back

    Returns:
        Complete audit trail with all data points
    """

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    dr.id as desk_run_id,
                    dr.run_timestamp,
                    dr.overall_sentiment,
                    t.id as ticker_analysis_id,
                    t.analysis_timestamp,
                    t.recommendation,
                    t.rationale,
                    t.avg_confidence,
                    t.negative_ratio,
                    t.positive_ratio,
                    t.related_news_count,
                    t.unique_entities_found,
                    t.top_risks_json,
                    t.top_opportunities_json,
                    d.id as decision_id,
                    d.decision_timestamp,
                    d.decision,
                    d.action_taken,
                    d.position_size,
                    d.entry_price,
                    d.exit_price,
                    d.profit_loss_pct,
                    d.status
                FROM ticker_analyses t
                JOIN investment_desk_runs dr ON t.desk_run_id = dr.id
                LEFT JOIN investment_decisions d ON t.id = d.ticker_analysis_id
                WHERE t.ticker = %s
                AND t.analysis_timestamp > CURRENT_TIMESTAMP - (INTERVAL '1 hour' * %s)
                ORDER BY t.analysis_timestamp DESC
            """, (ticker, hours_back))

            rows = cur.fetchall()

            audit_trail = []
            for row in rows:
                audit_dict = dict(row)
                # Parse JSON fields
                for field in ['top_risks_json', 'top_opportunities_json']:
                    if audit_dict.get(field):
                        try:
                            audit_dict[field.replace('_json', '')] = json.loads(audit_dict[field])
                        except:
                            pass
                audit_trail.append(audit_dict)

            return audit_trail
    finally:
        conn.close()
