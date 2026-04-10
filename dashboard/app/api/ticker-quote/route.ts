import { NextResponse } from 'next/server';

// Mock data for demo purposes - TODO: Replace with real Alpaca Data API
const MOCK_DATA: Record<string, any> = {
  'CCJ': { currentPrice: 42.50, change14d: 3.2, change28d: 8.5, volume: 2500000 },
  'BWXT': { currentPrice: 145.20, change14d: 1.5, change28d: 4.2, volume: 800000 },
  'CEG': { currentPrice: 210.80, change14d: 2.8, change28d: 12.3, volume: 1500000 },
  'UEC': { currentPrice: 8.45, change14d: -1.2, change28d: 5.7, volume: 1200000 },
  'EXC': { currentPrice: 38.90, change14d: 0.8, change28d: 6.1, volume: 3000000 },
  'SMR': { currentPrice: 3.25, change14d: -3.5, change28d: -8.2, volume: 5000000 },
};

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const ticker = searchParams.get('ticker');

  if (!ticker) {
    return NextResponse.json({ error: "Ticker parameter is required" }, { status: 400 });
  }

  const tickerUpper = ticker.toUpperCase();

  try {
    // Try to get from mock data first
    if (MOCK_DATA[tickerUpper]) {
      return NextResponse.json({
        ticker: tickerUpper,
        ...MOCK_DATA[tickerUpper],
        lastUpdate: new Date().toISOString(),
        dataSource: 'mock'
      });
    }

    // Generate reasonable mock data for other tickers
    const basePrice = 50 + Math.random() * 100;
    const change14d = (Math.random() - 0.5) * 10;
    const change28d = (Math.random() - 0.5) * 20;

    return NextResponse.json({
      ticker: tickerUpper,
      currentPrice: basePrice,
      change14d,
      change28d,
      volume: Math.floor(1000000 + Math.random() * 5000000),
      lastUpdate: new Date().toISOString(),
      dataSource: 'generated'
    });

  } catch (error) {
    console.error(`Error generating quote for ${ticker}:`, error);
    return NextResponse.json(
      { error: `Failed to generate quote for ${ticker}` },
      { status: 500 }
    );
  }
}
