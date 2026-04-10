import { NextRequest, NextResponse } from 'next/server';
import { pool } from '@/lib/db';

/**
 * GET /api/decisions
 * Get recent investment decisions from Decision Agent with full analysis data
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const limit = parseInt(searchParams.get('limit') || '10');
    const ticker = searchParams.get('ticker');

    let query = `
      SELECT
        d.id,
        d.desk_run_id,
        d.ticker,
        d.recommendation,
        d.desk_action,
        d.decision,
        d.decision_notes,
        d.action_taken,
        d.position_size,
        d.entry_price,
        d.alpaca_order_id,
        d.decision_timestamp,
        d.execution_timestamp,
        d.status,
        ta.full_results_json
      FROM investment_decisions d
      LEFT JOIN ticker_analyses ta ON d.ticker_analysis_id = ta.id
      WHERE 1=1
    `;

    const params: any[] = [];

    if (ticker) {
      params.push(ticker);
      query += ` AND d.ticker = $${params.length}`;
    }

    params.push(limit);
    query += `
      ORDER BY d.decision_timestamp DESC
      LIMIT $${params.length}
    `;

    const result = await pool.query(query, params);

    // Parse full_results_json and merge into response
    const decisions = result.rows.map(row => {
      const fullResults = row.full_results_json || {};
      const { full_results_json, ...decisionFields } = row;

      // Calculate sentiment score: range from -1 (100% bearish) to +1 (100% bullish)
      const positiveRatio = fullResults.positive_ratio ?? 0;
      const negativeRatio = fullResults.negative_ratio ?? 0;
      const sentimentScore = positiveRatio - negativeRatio;

      return {
        ...decisionFields,
        sentiment_score: sentimentScore,
        // Add full analysis data for UI (nested under 'analysis' key)
        analysis: {
          ...fullResults,
          bull_case: fullResults.bull_case || { arguments: [], deep_analysis: 'No positive signals detected' },
          bear_case: fullResults.bear_case || { arguments: [], deep_analysis: 'No negative signals detected' },
          risk_analysis: fullResults.risk_analysis || {},
          quant_stats: fullResults.quant_stats || {}
        }
      };
    });

    return NextResponse.json({
      success: true,
      decisions: decisions,
      meta: {
        count: decisions.length,
        ticker: ticker || 'all',
        limit: limit
      }
    });

  } catch (error: any) {
    console.error('❌ Error fetching decisions:', error);
    return NextResponse.json({
      success: false,
      error: error.message,
      decisions: []
    }, { status: 500 });
  }
}
