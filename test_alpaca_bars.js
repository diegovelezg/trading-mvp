// Test different parameters for bars endpoint
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

async function testBarsEndpoint() {
  const ticker = 'CCJ';

  console.log('Testing different parameters for bars endpoint:\n');

  // Test 1: Default
  console.log('1. Default parameters:');
  let result = await fetchFromAlpaca(`/stocks/${ticker}/bars?timeframe=1Day&limit=35`);
  console.log(`   Bars returned: ${result.bars?.length || 0}`);

  // Test 2: With start date
  console.log('\n2. With start date (30 days ago):');
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - 30);
  const startStr = startDate.toISOString();
  result = await fetchFromAlpaca(`/stocks/${ticker}/bars?timeframe=1Day&start=${startStr}`);
  console.log(`   Bars returned: ${result.bars?.length || 0}`);

  // Test 3: With end date
  console.log('\n3. With end date (today):');
  const endDate = new Date();
  const endStr = endDate.toISOString();
  result = await fetchFromAlpaca(`/stocks/${ticker}/bars?timeframe=1Day&end=${endStr}`);
  console.log(`   Bars returned: ${result.bars?.length || 0}`);

  // Test 4: With both start and end
  console.log('\n4. With start and end dates:');
  result = await fetchFromAlpaca(`/stocks/${ticker}/bars?timeframe=1Day&start=${startStr}&end=${endStr}`);
  console.log(`   Bars returned: ${result.bars?.length || 0}`);
  if (result.bars && result.bars.length > 0) {
    console.log(`   First bar: ${new Date(result.bars[0].t).toLocaleDateString()} - Close: $${result.bars[0].c}`);
    console.log(`   Last bar: ${new Date(result.bars[result.bars.length-1].t).toLocaleDateString()} - Close: $${result.bars[result.bars.length-1].c}`);
  }

  // Test 5: Check snapshot dailyBar
  console.log('\n5. Checking snapshot.dailyBar:');
  result = await fetchFromAlpaca(`/stocks/${ticker}/snapshot`);
  if (result.dailyBar) {
    console.log(`   DailyBar found: ${new Date(result.dailyBar.t).toLocaleDateString()}`);
    console.log(`   Close: $${result.dailyBar.c}, Volume: ${result.dailyBar.v}`);
  }
  if (result.prevDailyBar) {
    console.log(`   PrevDailyBar found: ${new Date(result.prevDailyBar.t).toLocaleDateString()}`);
    console.log(`   Close: $${result.prevDailyBar.c}`);
  }
}

testBarsEndpoint().catch(console.error);
