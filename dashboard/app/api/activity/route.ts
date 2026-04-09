import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const dateStr = searchParams.get('date');
  const limit = parseInt(searchParams.get('limit') || '20');

  try {
    let query = `
      SELECT 
        d.id as decision_id,
        d.ticker,
        d.recommendation,
        d.desk_action,
        d.decision_timestamp,
        d.decision_notes,
        d.action_taken,
        d.target_price,
        d.stop_loss,
        d.position_size,
        d.status,
        d.alpaca_order_id,
        t.avg_confidence,
        t.rationale,
        t.full_results_json as analysis_json,
        dr.overall_sentiment as desk_sentiment
      FROM investment_decisions d
      JOIN ticker_analyses t ON d.ticker_analysis_id = t.id
      JOIN investment_desk_runs dr ON d.desk_run_id = dr.id
    `;

    const params: any[] = [];
    if (dateStr) {
      // Adjusted for UTC-5 offset to match local system time
      query += ` WHERE date(d.decision_timestamp, '-5 hours') = ?`;
      params.push(dateStr);
    }

    query += ` ORDER BY d.decision_timestamp DESC LIMIT ?`;
    params.push(limit);

    const activities = db.prepare(query).all(...params);

    // Parse JSON fields
    const parsedActivities = activities.map((act: any) => ({
      ...act,
      analysis: act.analysis_json ? JSON.parse(act.analysis_json) : null
    }));

    return NextResponse.json(parsedActivities);
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
