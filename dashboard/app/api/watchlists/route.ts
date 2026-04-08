import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET() {
  try {
    // Fetch active watchlists with their items
    const watchlists = db.prepare(`
      SELECT 
        w.id, 
        w.name, 
        w.description, 
        w.criteria_summary,
        w.created_at,
        (SELECT COUNT(*) FROM watchlist_items WHERE watchlist_id = w.id) as ticker_count
      FROM watchlists w
      WHERE w.status = 'active'
      ORDER BY w.created_at DESC
    `).all() as any[];

    // For each watchlist, get the tickers
    const watchlistsWithItems = watchlists.map(wl => {
      const items = db.prepare(`
        SELECT ticker, company_name, reason, added_at
        FROM watchlist_items
        WHERE watchlist_id = ?
        ORDER BY added_at DESC
      `).all(wl.id);
      
      return { ...wl, items };
    });

    return NextResponse.json(watchlistsWithItems);
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
