import { supabase } from '@/lib/supabase';
import { withErrorHandler } from '@/lib/api-error-handler';
import { successResponse } from '@/lib/api-response';

const API_KEY = process.env.ALPACA_PAPER_API_KEY;
const SECRET_KEY = process.env.PAPER_API_SECRET;
const BASE_URL = 'https://paper-api.alpaca.markets';

/**
 * GET /api/stats
 *
 * Obtener estadísticas de la cuenta y portfolio
 */
export const GET = withErrorHandler(async () => {
  if (!API_KEY || !SECRET_KEY) {
    throw new Error('Missing Alpaca Credentials');
  }

  const headers = {
    'APCA-API-KEY-ID': API_KEY,
    'APCA-API-SECRET-KEY': SECRET_KEY,
  };

  // 1. Fetch REAL account data from Alpaca (The Source of Truth)
  const accountRes = await fetch(`${BASE_URL}/v2/account`, { headers });
  const account = await accountRes.json();

  // 2. Fetch REAL portfolio history for Sharpe and P&L
  const historyRes = await fetch(`${BASE_URL}/v2/account/portfolio/history?period=1M&timeframe=1D`, { headers });
  const history = await historyRes.json();

  // 3. Extract metrics from real equity curve
  const equity = parseFloat(account.equity);
  const baseValue = history.base_value || 100000; // Use Alpaca's base_value, not first equity point
  const totalPL = equity - baseValue;
  const returnPct = baseValue !== 0 ? (totalPL / baseValue) * 100 : 0;

  // Calculate Max Drawdown from history
  let maxDrawdown = 0;
  let peak = history.equity[0] || equity;
  for (let i = 0; i < history.equity.length; i++) {
    if (history.equity[i] > peak) peak = history.equity[i];
    const dd = peak !== 0 ? (peak - history.equity[i]) / peak : 0;
    if (dd > maxDrawdown) maxDrawdown = dd;
  }
  maxDrawdown = maxDrawdown * 100;

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
  const [newsRes, runsRes] = await Promise.all([
    supabase.from('news').select('*', { count: 'exact', head: true }),
    supabase.from('investment_desk_runs').select('*', { count: 'exact', head: true })
  ]);

  // 5. Fetch ALL decisions from Supabase to compute Win Rate, Profit Factor, and Totals
  const { data: allDecisions } = await supabase
    .from('investment_decisions')
    .select('*');

  let profitFactor = 0;
  let winRate = 0;
  let totalDecisions = 0;

  if (allDecisions && allDecisions.length > 0) {
    totalDecisions = allDecisions.length;
    
    // Closed decisions are transactions that have a profit_loss
    const closedDecisions = allDecisions.filter(d => d.status === 'CLOSED');
    
    if (closedDecisions.length > 0) {
      let grossProfit = 0;
      let grossLoss = 0;
      let wins = 0;

      closedDecisions.forEach(d => {
        const pl = parseFloat(d.profit_loss) || 0;
        if (pl > 0) {
          grossProfit += pl;
          wins += 1;
        }
        if (pl < 0) {
          grossLoss += Math.abs(pl);
        }
      });
      
      profitFactor = grossLoss === 0 ? (grossProfit > 0 ? 999 : 0) : (grossProfit / grossLoss);
      winRate = (wins / closedDecisions.length) * 100;
    }
  }

  // Format history for charting
  const equityHistory = history.timestamp.map((ts: number, i: number) => ({
    time: new Date(ts * 1000).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }),
    equity: history.equity[i] !== null ? history.equity[i] : equity
  })).filter((point: any) => point.equity > 0);

  // Add current equity point to ensure chart shows latest value
  equityHistory.push({
    time: new Date().toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }),
    equity: equity
  });

  return successResponse({
    equity: round(equity, 2),
    profitFactor: round(profitFactor, 2),
    totalPL: round(totalPL, 2),
    returnPct: round(returnPct, 2),
    maxDrawdown: round(maxDrawdown, 2),
    sharpeRatio: round(sharpe, 2),
    winRate: round(winRate, 1),
    newsProcessed: newsRes.count || 0,
    deskRuns: runsRes.count || 0,
    totalDecisions: totalDecisions,
    equityHistory: equityHistory
  });
});

function round(num: number, decimals: number) {
  return Math.round(num * Math.pow(10, decimals)) / Math.pow(10, decimals);
}
