import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ ticker: string }> }
) {
  try {
    const { ticker } = await params;
    const body = await request.json();
    const { watchlist_id, company_name, reason } = body;

    if (!watchlist_id) {
      return NextResponse.json(
        { error: 'watchlist_id is required' },
        { status: 400 }
      );
    }

    const { data: item, error } = await supabase
      .from('watchlist_items')
      .update({
        company_name: company_name || null,
        reason: reason || null
      })
      .eq('watchlist_id', parseInt(watchlist_id))
      .eq('ticker', ticker.toUpperCase())
      .select()
      .single();

    if (error) throw error;

    if (!item) {
      return NextResponse.json(
        { error: 'Item not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(item);
  } catch (error: any) {
    console.error('API Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
