import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

api_key = os.getenv("ALPACA_PAPER_API_KEY")
secret_key = os.getenv("PAPER_API_SECRET")
client = StockHistoricalDataClient(api_key, secret_key)

end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
start_date = end_date - timedelta(days=400)

request_params = StockBarsRequest(
    symbol_or_symbols=["USO", "SPY"],
    timeframe=TimeFrame.Day,
    start=start_date,
    end=end_date
)

bars = client.get_stock_bars(request_params)
df = bars.df

ticker_df = df.xs("USO").copy()
spy_df = df.xs("SPY").copy()

ticker_returns = ticker_df['close'].pct_change()
spy_returns = spy_df['close'].pct_change()

combined = pd.concat([ticker_returns, spy_returns], axis=1).dropna()
combined.columns = ['ticker', 'spy']

rolling_window = 60
cov = combined['ticker'].rolling(window=rolling_window).cov(combined['spy'])
var = combined['spy'].rolling(window=rolling_window).var()
beta_rolling = cov / var

print("Last Covariance:", cov.iloc[-1])
print("Last Variance:", var.iloc[-1])
print("Last Beta:", beta_rolling.iloc[-1])
print("Last 5 days returns:")
print(combined.tail())
