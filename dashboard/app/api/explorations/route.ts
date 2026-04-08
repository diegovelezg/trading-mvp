import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET() {
  try {
    const explorations = db.prepare(`
      SELECT 
        id, 
        prompt, 
        criteria, 
        tickers, 
        reasoning, 
        timestamp
      FROM explorations
      ORDER BY timestamp DESC
    `).all() as any[];

    // Parse tickers from JSON string with safety check
    const parsedExplorations = explorations.map(exp => {
      let parsedTickers = [];
      try {
        parsedTickers = JSON.parse(exp.tickers || '[]');
        if (!Array.isArray(parsedTickers)) {
          // Handle case where it's a single string or non-array JSON
          parsedTickers = typeof parsedTickers === 'string' ? [parsedTickers] : [];
        }
      } catch (e) {
        // Fallback for comma-separated strings if any exist
        parsedTickers = exp.tickers ? exp.tickers.split(',').map((t: string) => t.trim()) : [];
      }
      
      return {
        ...exp,
        tickers: parsedTickers
      };
    });

    return NextResponse.json(parsedExplorations);
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
