import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { watchlist_id, ticker, company_name, reason } = body;

    if (!watchlist_id || !ticker) {
      return NextResponse.json({ error: 'watchlist_id and ticker are required' }, { status: 400 });
    }

    const { data: item, error } = await supabase
      .from('watchlist_items')
      .insert({
        watchlist_id: parseInt(watchlist_id),
        ticker: ticker.toUpperCase(),
        company_name: company_name || null,
        reason: reason || null
      })
      .select()
      .single();

    if (error) throw error;

    return NextResponse.json(item, { status: 201 });
  } catch (error: any) {
    console.error('API Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function DELETE(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const ticker = searchParams.get('ticker');
    const watchlistId = searchParams.get('watchlistId');

    if (!ticker || !watchlistId) {
      return NextResponse.json({ error: "Missing ticker or watchlistId" }, { status: 400 });
    }

    const { error } = await supabase
      .from('watchlist_items')
      .delete()
      .eq('watchlist_id', watchlistId)
      .eq('ticker', ticker.toUpperCase());

    if (error) throw error;

    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('API Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
