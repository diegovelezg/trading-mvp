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
          rationale,
          full_results_json
        ),
        investment_desk_runs (
          overall_sentiment
        )
      `);

    if (dateStr) {
      // Adjusted for UTC-5 offset to match local system time (SQLite used date(..., '-5 hours'))
      // To match SQLite's logic: date(decision_timestamp - 5h) = dateStr
      // That means decision_timestamp is between (dateStrT00:00:00 + 5h) and (dateStrT23:59:59 + 5h)
      const startOfDay = new Date(`${dateStr}T00:00:00Z`);
      startOfDay.setUTCHours(startOfDay.getUTCHours() + 5);
      
      const endOfDay = new Date(`${dateStr}T23:59:59.999Z`);
      endOfDay.setUTCHours(endOfDay.getUTCHours() + 5);

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
