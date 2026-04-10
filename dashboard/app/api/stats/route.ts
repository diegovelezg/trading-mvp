import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

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

    // 4. Intelligence Metadata (From Supabase)
    const [newsRes, runsRes, decisionsRes] = await Promise.all([
      supabase.from('news').select('*', { count: 'exact', head: true }),
      supabase.from('investment_desk_runs').select('*', { count: 'exact', head: true }),
      supabase.from('investment_decisions').select('*', { count: 'exact', head: true })
    ]);

    // 5. Calculate Win Rate from Alpaca Activities (Recent 50 fills)
    const activitiesRes = await fetch(`${BASE_URL}/v2/account/activities?activity_types=FILL&page_size=50`, { headers });
    const activities = await activitiesRes.json();
    
    let winRate = 0;
    if (Array.isArray(activities) && activities.length > 0) {
      // Simple logic: match buy/sell for the same ticker in the recent list
      const trades: number[] = [];
      const symbols = [...new Set(activities.map(a => a.symbol))];
      
      symbols.forEach(symbol => {
        const fills = activities.filter(a => a.symbol === symbol).sort((a, b) => 
          new Date(a.transaction_time).getTime() - new Date(b.transaction_time).getTime()
        );
        
        // Match consecutive buy/sell or sell/buy pairs in this window
        for (let i = 0; i < fills.length - 1; i++) {
          const current = fills[i];
          const next = fills[i+1];
          
          if (current.side !== next.side) {
            const buyPrice = current.side === 'buy' ? parseFloat(current.price) : parseFloat(next.price);
            const sellPrice = current.side === 'sell' ? parseFloat(current.price) : parseFloat(next.price);
            trades.push(sellPrice - buyPrice);
            i++; // Skip next as it's matched
          }
        }
      });
      
      if (trades.length > 0) {
        const wins = trades.filter(t => t > 0).length;
        winRate = (wins / trades.length) * 100;
      }
    }

    return NextResponse.json({
      equity: round(equity, 2),
      buyingPower: round(parseFloat(account.buying_power), 2),
      totalPL: round(totalPL, 2),
      sharpeRatio: round(sharpe, 2),
      winRate: round(winRate, 1),
      newsProcessed: newsRes.count || 0,
      deskRuns: runsRes.count || 0,
      totalDecisions: decisionsRes.count || 0
    });
  } catch (error: any) {
    console.error('Stats API Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

function round(num: number, decimals: number) {
  return Math.round(num * Math.pow(10, decimals)) / Math.pow(10, decimals);
}
