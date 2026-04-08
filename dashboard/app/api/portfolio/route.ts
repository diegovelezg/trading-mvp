import { NextResponse } from 'next/server';

const API_KEY = process.env.ALPACA_PAPER_API_KEY;
const SECRET_KEY = process.env.PAPER_API_SECRET;
const BASE_URL = 'https://paper-api.alpaca.markets';

export async function GET() {
  if (!API_KEY || !SECRET_KEY) {
    return NextResponse.json({ error: "Missing Alpaca Credentials" }, { status: 500 });
  }

  const headers = {
    'APCA-API-KEY-ID': API_KEY,
    'APCA-API-SECRET-KEY': SECRET_KEY,
    'Content-Type': 'application/json',
  };

  try {
    // 1. Get Account Info
    const accountRes = await fetch(`${BASE_URL}/v2/account`, { headers });
    const account = await accountRes.json();

    // 2. Get Current Positions
    const positionsRes = await fetch(`${BASE_URL}/v2/positions`, { headers });
    const positions = await positionsRes.json();

    // 3. Get Open Orders (NEW)
    const ordersRes = await fetch(`${BASE_URL}/v2/orders?status=open`, { headers });
    const orders = await ordersRes.json();

    return NextResponse.json({
      equity: parseFloat(account.equity),
      cash: parseFloat(account.cash),
      buying_power: parseFloat(account.buying_power),
      portfolio_value: parseFloat(account.portfolio_value),
      positions: Array.isArray(positions) ? positions : [],
      orders: Array.isArray(orders) ? orders : []
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
