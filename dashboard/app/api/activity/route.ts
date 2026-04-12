import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const dateStr = searchParams.get('date');
  const limit = parseInt(searchParams.get('limit') || '20');

  try {
    let query = supabase
      .from('investment_decisions')
      .select(`
        id,
        desk_run_id,
        ticker,
        recommendation,
        desk_action,
        decision_timestamp,
        decision_notes,
        action_taken,
        target_price,
        stop_loss,
        position_size,
        status,
        alpaca_order_id,
        ticker_analyses (
          avg_confidence,
          positive_ratio,
          negative_ratio,
          rationale,
          full_results_json
        ),
        investment_desk_runs (
          overall_sentiment
        )
      `);

    if (dateStr) {
      // Simple UTC date range - decision_timestamp is already in UTC
      const startOfDay = new Date(`${dateStr}T00:00:00.000Z`);
      const endOfDay = new Date(`${dateStr}T23:59:59.999Z`);

      query = query
        .gte('decision_timestamp', startOfDay.toISOString())
        .lte('decision_timestamp', endOfDay.toISOString());
    }

    const { data: activities, error } = await query
      .order('decision_timestamp', { ascending: false })
      .limit(limit);

    if (error) throw error;

    // Parse JSON fields and flatten joined tables
    const parsedActivities = (activities || []).map((act: any) => ({
      decision_id: act.id,
      desk_run_id: act.desk_run_id,
      ticker: act.ticker,
      recommendation: act.recommendation,
      desk_action: act.desk_action,
      decision_timestamp: act.decision_timestamp,
      decision_notes: act.decision_notes,
      action_taken: act.action_taken,
      target_price: act.target_price,
      stop_loss: act.stop_loss,
      position_size: act.position_size,
      status: act.status,
      alpaca_order_id: act.alpaca_order_id,
      avg_confidence: act.ticker_analyses?.avg_confidence,
      sentiment_score: (act.ticker_analyses?.positive_ratio || 0) - (act.ticker_analyses?.negative_ratio || 0),
      confidence_in_decision: act.ticker_analyses?.avg_confidence,
      rationale: act.ticker_analyses?.rationale,
      analysis: act.ticker_analyses?.full_results_json,
      desk_sentiment: act.investment_desk_runs?.overall_sentiment
    }));

    return NextResponse.json(parsedActivities);
  } catch (error: any) {
    console.error('Activity API Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
