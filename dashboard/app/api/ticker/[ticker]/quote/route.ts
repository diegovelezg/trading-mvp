import { NextResponse } from 'next/server';

const API_KEY = process.env.ALPACA_PAPER_API_KEY;
const SECRET_KEY = process.env.PAPER_API_SECRET;
const BASE_URL = 'https://paper-api.alpaca.markets';

export async function GET(
  request: Request,
  { params }: { params: { ticker: string } }
) {
  const { ticker } = params;

  if (!API_KEY || !SECRET_KEY) {
    return NextResponse.json({ error: "Missing Alpaca Credentials" }, { status: 500 });
  }

  if (!ticker) {
    return NextResponse.json({ error: "Ticker parameter is required" }, { status: 400 });
  }

  const headers = {
    'APCA-API-KEY-ID': API_KEY,
    'APCA-API-SECRET-KEY': SECRET_KEY,
    'Content-Type': 'application/json',
  };

  try {
    console.log(`Fetching quote for ${ticker}...`);

    // Get current price from snapshots
    const snapshotsRes = await fetch(`${BASE_URL}/v2/stocks/${ticker}/snapshots`, { headers });
    const snapshotsData = await snapshotsRes.json();

    console.log(`Snapshots response for ${ticker}:`, JSON.stringify(snapshotsData).substring(0, 200));

    if (!snapshotsRes.ok || !snapshotsData.latestTrade) {
      return NextResponse.json({ error: `Failed to fetch data for ${ticker}` }, { status: 404 });
    }

    const latestTrade = snapshotsData.latestTrade;
    const dailyBar = snapshotsData.dailyBar;

    // Calculate changes
    const currentPrice = latestTrade.p;
    const change14d = dailyBar ? ((currentPrice - dailyBar.c) / dailyBar.c) * 100 : 0;
    const change28d = dailyBar ? ((currentPrice - dailyBar.o) / dailyBar.o) * 100 : 0;

    // Get volume from daily bar
    const volume = dailyBar?.v || 0;

    const result = {
      ticker: ticker.toUpperCase(),
      currentPrice,
      change14d,
      change28d,
      volume,
      previousClose: dailyBar?.c || currentPrice,
      lastUpdate: new Date().toISOString()
    };

    console.log(`Quote result for ${ticker}:`, result);

    return NextResponse.json(result);

  } catch (error) {
    console.error(`Error fetching quote for ${ticker}:`, error);
    return NextResponse.json(
      { error: `Failed to fetch quote for ${ticker}: ${error}` },
      { status: 500 }
    );
  }
}
