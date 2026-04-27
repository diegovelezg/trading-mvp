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

  // Calculate Max Drawdown from history (filter out zeros/nulls)
  let maxDrawdown = 0;
  const validEquity = history.equity.filter((e: number) => e > 0);

  if (validEquity.length > 0) {
    let peak = validEquity[0];
    for (let i = 0; i < validEquity.length; i++) {
      if (validEquity[i] > peak) peak = validEquity[i];
      const dd = peak !== 0 ? (peak - validEquity[i]) / peak : 0;
      if (dd > maxDrawdown) maxDrawdown = dd;
    }
    maxDrawdown = maxDrawdown * 100;
  }

  // Calculate a simple Sharpe from daily equity (use same filtered data)
  const returns = [];
  for (let i = 1; i < validEquity.length; i++) {
    returns.push((validEquity[i] - validEquity[i-1]) / validEquity[i-1]);
  }
  const avgReturn = returns.length > 0 ? returns.reduce((a, b) => a + b, 0) / returns.length : 0;
  const stdDev = returns.length > 0 ? Math.sqrt(returns.map(x => Math.pow(x - avgReturn, 2)).reduce((a, b) => a + b, 0) / returns.length) : 0;
  const sharpe = stdDev !== 0 ? (avgReturn / stdDev) * Math.sqrt(252) : 0;

  // 4. Intelligence Metadata (From Supabase)
  const [newsRes, runsRes, decisionsRes] = await Promise.all([
    supabase.from('news').select('*', { count: 'exact', head: true }),
    supabase.from('investment_desk_runs').select('*', { count: 'exact', head: true }),
    supabase.from('investment_decisions').select('*', { count: 'exact', head: true })
  ]);

  // 5. Fetch closed orders from Alpaca (SSOT) to compute Win Rate and Profit Factor
  const ordersRes = await fetch(`${BASE_URL}/v2/orders?status=closed&limit=500`, { headers });
  const orders = await ordersRes.json();

  let profitFactor = 0;
  let winRate = 0;
  let totalCompletedTrades = 0;

  if (Array.isArray(orders) && orders.length > 0) {
    // Group orders by symbol and pair buy/sell (FIFO)
    const tradesBySymbol: { [key: string]: Array<{ side: string; qty: number; price: number; timestamp: number }> } = {};

    orders.forEach((order: any) => {
      const qty = parseFloat(order.filled_qty) || parseFloat(order.qty);
      const price = parseFloat(order.filled_avg_price) || parseFloat(order.limit_price);

      // Skip orders with no quantity or no price (not filled)
      if ((order.side === 'buy' || order.side === 'sell') && qty > 0 && price > 0) {
        const symbol = order.symbol;
        if (!tradesBySymbol[symbol]) {
          tradesBySymbol[symbol] = [];
        }
        tradesBySymbol[symbol].push({
          side: order.side,
          qty: qty,
          price: price,
          timestamp: new Date(order.created_at).getTime()
        });
      }
    });

    // Pair buys with sells (FIFO) and calculate P&L
    let grossProfit = 0;
    let grossLoss = 0;
    let wins = 0;

    Object.values(tradesBySymbol).forEach((symbolOrders) => {
      // Sort by timestamp
      symbolOrders.sort((a, b) => a.timestamp - b.timestamp);

      const buyQueue: Array<{ qty: number; price: number }> = [];

      symbolOrders.forEach((order) => {
        if (order.side === 'buy') {
          buyQueue.push({ qty: order.qty, price: order.price });
        } else if (order.side === 'sell') {
          let remainingQty = order.qty;

          // Match with FIFO buys
          while (remainingQty > 0 && buyQueue.length > 0) {
            const buy = buyQueue[0]!;
            const matchedQty = Math.min(remainingQty, buy.qty);

            // Calculate P&L for this matched pair
            const profitLoss = (order.price - buy.price) * matchedQty;

            if (profitLoss > 0) {
              grossProfit += profitLoss;
              wins += 1;
            } else if (profitLoss < 0) {
              grossLoss += Math.abs(profitLoss);
            }

            totalCompletedTrades++;

            // Update quantities
            remainingQty -= matchedQty;
            buy.qty -= matchedQty;

            // Remove fully matched buy from queue
            if (buy.qty <= 0) {
              buyQueue.shift();
            }
          }
        }
      });
    });

    // Calculate final metrics
    if (totalCompletedTrades > 0) {
      profitFactor = grossLoss === 0 ? (grossProfit > 0 ? 999 : 0) : grossProfit / grossLoss;
      winRate = (wins / totalCompletedTrades) * 100;
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
    totalDecisions: decisionsRes.count || 0,
    totalOperations: totalCompletedTrades || 0,
    equityHistory: equityHistory
  });
});

function round(num: number, decimals: number) {
  return Math.round(num * Math.pow(10, decimals)) / Math.pow(10, decimals);
}
