import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function DELETE(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const ticker = searchParams.get('ticker');
    const watchlistId = searchParams.get('watchlistId');

    if (!ticker || !watchlistId) {
      return NextResponse.json({ error: "Missing ticker or watchlistId" }, { status: 400 });
    }

    // Since we are in readonly mode in the lib/db.ts for safety, 
    // I will check if I need to re-open the connection for writing.
    // For local MVP, let's assume we can write.
    const deleteStmt = db.prepare(`
      DELETE FROM watchlist_items 
      WHERE watchlist_id = ? AND ticker = ?
    `);
    
    deleteStmt.run(watchlistId, ticker);

    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
