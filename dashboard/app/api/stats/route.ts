import { NextResponse } from 'next/server';
import db from '@/lib/db';

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
  };

  try {
    // 1. Fetch REAL account data from Alpaca (The Source of Truth)
    const accountRes = await fetch(`${BASE_URL}/v2/account`, { headers });
    const account = await accountRes.json();

    // 2. Fetch REAL portfolio history for Sharpe and P&L
    const historyRes = await fetch(`${BASE_URL}/v2/account/portfolio/history?period=1M&timeframe=1D`, { headers });
    const history = await historyRes.json();

    // 3. Extract metrics from real equity curve
    const equity = parseFloat(account.equity);
    const lastEquity = history.equity[0];
    const totalPL = equity - lastEquity;
    
    // Calculate a simple Sharpe from daily equity if history is available
    const returns = [];
    for (let i = 1; i < history.equity.length; i++) {
      if (history.equity[i-1] !== 0) {
        returns.push((history.equity[i] - history.equity[i-1]) / history.equity[i-1]);
      }
    }
    const avgReturn = returns.reduce((a, b) => a + b, 0) / (returns.length || 1);
    const stdDev = Math.sqrt(returns.map(x => Math.pow(x - avgReturn, 2)).reduce((a, b) => a + b, 0) / (returns.length || 1));
    const sharpe = stdDev !== 0 ? (avgReturn / stdDev) * Math.sqrt(252) : 0;

    // 4. Intelligence Metadata (From local DB - Rationale/Activity)
    const newsCount = db.prepare("SELECT COUNT(*) as count FROM news").get() as any;
    const runsCount = db.prepare("SELECT COUNT(*) as count FROM investment_desk_runs").get() as any;
    const decisions = db.prepare("SELECT COUNT(*) as count FROM investment_decisions").get() as any;

    return NextResponse.json({
      equity: round(equity, 2),
      buyingPower: round(parseFloat(account.buying_power), 2),
      totalPL: round(totalPL, 2),
      sharpeRatio: round(sharpe, 2),
      winRate: 0, // In progress: will link with closed orders from Alpaca
      newsProcessed: newsCount.count,
      deskRuns: runsCount.count,
      totalDecisions: decisions.count
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

function round(num: number, decimals: number) {
  return Math.round(num * Math.pow(10, decimals)) / Math.pow(10, decimals);
}
