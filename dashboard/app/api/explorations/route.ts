import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET() {
  try {
    const { data: explorations, error } = await supabase
      .from('explorations')
      .select('id, prompt, criteria, tickers, reasoning, created_at')
      .order('created_at', { ascending: false });

    if (error) throw error;

    // Parse tickers from JSONB (Supabase automatically parses it)
    const parsedExplorations = (explorations || []).map(exp => ({
      id: exp.id,
      prompt: exp.prompt,
      criteria: exp.criteria,
      reasoning: exp.reasoning,
      timestamp: exp.created_at, // Map created_at to timestamp for backward compatibility
      tickers: Array.isArray(exp.tickers) ? exp.tickers : []
    }));

    return NextResponse.json(parsedExplorations);
  } catch (error: any) {
    console.error('Explorations API Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
