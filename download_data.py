import requests
import pandas as pd
from datetime import datetime

TOKEN_ADDRESS = "Ax8PSfCXxmxb8C8kYTzN5CPpTe6PyeZfFf8rrXNCjupx"

def download_from_dexscreener():
    print("📥 Trying Dexscreener for historical data...")

    url = f"https://api.dexscreener.com/latest/dex/tokens/{TOKEN_ADDRESS}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Dexscreener API error")
        return None

    data = response.json()
    pairs = data.get("pairs", [])
    
    if not pairs:
        print("❌ No trading pairs found")
        return None

    pair = max(pairs, key=lambda x: x.get("liquidity", {}).get("usd", 0))
    print(f"Found pair: {pair.get('baseToken', {}).get('symbol')} / {pair.get('quoteToken', {}).get('symbol')}")
    print(f"Liquidity: ${pair.get('liquidity', {}).get('usd', 0):,}")
    print(f"Current Price: ${pair.get('priceUsd')}")

    # Create dummy historical data for backtesting (with fixed frequency)
    print("\nCreating dummy historical data for backtester...")
    
    dates = pd.date_range(end=datetime.now(), periods=400, freq='15min')
    
    # Simulate some price movement
    import numpy as np
    base_price = float(pair.get('priceUsd', 0.001))
    prices = base_price * (1 + np.cumsum(np.random.normal(0, 0.008, 400)))
    
    df = pd.DataFrame({
        'open': prices,
        'high': prices * 1.015,
        'low': prices * 0.985,
        'close': prices,
        'volume': [8000 + i*50 for i in range(400)]
    }, index=dates)
    
    df.to_csv("historical_data.csv")
    print("✅ Success! Created historical_data.csv with 400 candles")
    print(df.tail(5))
    return df

if __name__ == "__main__":
    download_from_dexscreener()
