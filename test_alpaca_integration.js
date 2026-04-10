// Test script for Alpaca Data API integration
// Run with: node test_alpaca_integration.js

const ALPACA_PAPER_API_KEY = 'YOUR_ALPACA_PAPER_API_KEY';
const PAPER_API_SECRET = 'YOUR_ALPACA_SECRET_KEY';
const ALPACA_DATA_BASE_URL = 'https://data.alpaca.markets/v2';

async function fetchFromAlpaca(endpoint) {
  const response = await fetch(`${ALPACA_DATA_BASE_URL}${endpoint}`, {
    headers: {
      'APCA-API-KEY-ID': ALPACA_PAPER_API_KEY,
      'APCA-API-SECRET-KEY': PAPER_API_SECRET,
    },
  });

  if (!response.ok) {
    throw new Error(`Alpaca API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

function calculate28DayChange(currentPrice, historicalPrice) {
  if (!historicalPrice || historicalPrice === 0) return 0;
  return ((currentPrice - historicalPrice) / historicalPrice) * 100;
}

async function getTickerData(ticker) {
  try {
    console.log(`\n📊 Fetching data for ${ticker}...`);

    // 1. Get current snapshot
    const snapshot = await fetchFromAlpaca(`/stocks/${ticker}/snapshot`);
    console.log('  ✓ Snapshot retrieved');

    // 2. Get historical bars
    const barsResponse = await fetchFromAlpaca(
      `/stocks/${ticker}/bars?timeframe=1Day&limit=35`
    );
    const bars = barsResponse.bars || [];
    console.log(`  ✓ Retrieved ${bars.length} historical bars`);

    // 3. Extract current price
    const currentPrice = snapshot.latestTrade?.p || snapshot.dailyBar?.c;
    if (!currentPrice) {
      throw new Error('No price data available');
    }
    console.log(`  💰 Current price: $${currentPrice}`);

    // 4. Calculate 28-day change
    let change28d = 0;
    if (bars.length >= 28) {
      const price28DaysAgo = bars[bars.length - 28].c;
      change28d = calculate28DayChange(currentPrice, price28DaysAgo);
      console.log(`  📈 28-day change: ${change28d.toFixed(2)}%`);
    } else if (bars.length > 0) {
      const oldestPrice = bars[0].c;
      change28d = calculate28DayChange(currentPrice, oldestPrice);
      console.log(`  📈 ${bars.length}-day change: ${change28d.toFixed(2)}%`);
    }

    // 5. Get volume
    const volume = snapshot.dailyBar?.v || snapshot.latestTrade?.s || 0;
    console.log(`  📊 Volume: ${volume.toLocaleString()}`);

    return {
      ticker,
      currentPrice,
      change28d,
      volume,
      success: true
    };
  } catch (error) {
    console.error(`  ❌ Error: ${error.message}`);
    return { ticker, success: false, error: error.message };
  }
}

async function main() {
  console.log('🚀 Testing Alpaca Data API Integration\n');
  console.log('Testing tickers: CCJ, NXE, UEC, INVALID\n');

  const tickers = ['CCJ', 'NXE', 'UEC', 'INVALID'];

  for (const ticker of tickers) {
    await getTickerData(ticker);
  }

  console.log('\n✅ Test complete!');
}

main().catch(console.error);
