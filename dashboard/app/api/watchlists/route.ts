import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { name, description, criteria_prompt, criteria_summary } = body;

    if (!name) {
      return NextResponse.json({ error: 'Name is required' }, { status: 400 });
    }

    const { data: watchlist, error } = await supabase
      .from('watchlists')
      .insert({
        name,
        description: description || null,
        criteria_prompt: criteria_prompt || null,
        criteria_summary: criteria_summary || null,
        status: 'active'
      })
      .select()
      .single();

    if (error) throw error;

    return NextResponse.json(watchlist, { status: 201 });
  } catch (error: any) {
    console.error('API Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function GET() {
  try {
    // Fetch active watchlists with a count of their items
    // Since we're using Supabase client, we can join or use count()
    const { data: watchlists, error } = await supabase
      .from('watchlists')
      .select(`
        id,
        name,
        description,
        criteria_summary,
        created_at,
        watchlist_items(count)
      `)
      .eq('status', 'active')
      .order('created_at', { ascending: false });

    if (error) throw error;

    // Fetch items for each watchlist in parallel with live Alpaca data
    const watchlistsWithItems = await Promise.all(
      watchlists.map(async (wl: any) => {
        const { data: items, error: itemsError } = await supabase
          .from('watchlist_items')
          .select('ticker, company_name, reason, added_at')
          .eq('watchlist_id', wl.id)
          .order('added_at', { ascending: false });

        if (itemsError) throw itemsError;

        // Get live ticker data from Alpaca
        const tickers = items.map(item => item.ticker);
        const { getBatchTickerData } = await import('@/lib/alpaca');
        const liveData = await getBatchTickerData(tickers);

        // Merge static data with live data
        const itemsWithLive = items.map(item => {
          const live = liveData.find(d => d.ticker === item.ticker);
          return {
            ...item,
            currentPrice: live?.currentPrice,
            change28d: live?.change28d,
            volume: live?.volume,
            lastUpdated: live?.lastUpdated,
          };
        });

        // Simplify ticker_count from the count join
        const ticker_count = wl.watchlist_items?.[0]?.count || 0;

        return { ...wl, ticker_count, items: itemsWithLive };
      })
    );

    return NextResponse.json(watchlistsWithItems);
  } catch (error: any) {
    console.error('API Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
