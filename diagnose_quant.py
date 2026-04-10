
import os
import pandas as pd
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

load_dotenv()

def diagnose():
    api_key = os.getenv("ALPACA_PAPER_API_KEY")
    secret_key = os.getenv("PAPER_API_SECRET")
    
    client = StockHistoricalDataClient(api_key, secret_key)
    
    # Pedimos los últimos 10 días para tener contexto
    end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=15)
    
    print(f"Diagnosing AAPL from {start.date()} to {end.date()}...")
    
    request = StockBarsRequest(
        symbol_or_symbols="AAPL", 
        timeframe=TimeFrame.Day, 
        start=start, 
        end=end
    )
    
    bars = client.get_stock_bars(request)
    df = bars.df.xs("AAPL")
    
    print("\n--- RAW DATA FROM ALPACA ---")
    print(df[['open', 'high', 'low', 'close']].tail(5))
    
    # Análisis de Volatilidad (Rango Diario)
    df['range'] = df['high'] - df['low']
    avg_range = df['range'].mean()
    
    print(f"\nAverage Daily Range (Last 10 bars): ${avg_range:.2f}")
    
    # Cálculo manual del último True Range
    last_idx = -1
    last_bar = df.iloc[last_idx]
    prev_close = df.iloc[last_idx - 1]['close']
    
    tr = max(
        last_bar['high'] - last_bar['low'],
        abs(last_bar['high'] - prev_close),
        abs(last_bar['low'] - prev_close)
    )
    
    print(f"Last Bar Date: {df.index[last_idx]}")
    print(f"Last Bar High: ${last_bar['high']:.2f}")
    print(f"Last Bar Low:  ${last_bar['low']:.2f}")
    print(f"Prev Bar Close: ${prev_close:.2f}")
    print(f"Calculated True Range (Manual): ${tr:.2f}")

if __name__ == "__main__":
    diagnose()
