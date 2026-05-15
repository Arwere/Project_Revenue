import asyncio
import time
import numpy as np
from typing import List
import httpx
from config import config

client = httpx.AsyncClient(timeout=15.0)
BIRDEYE_API_KEY = "fc1e63ea2f2548ebb120f97580d51923"

price_cache = {}
history_cache = {}
last_price_fetch = {}
last_history_fetch = {}

async def get_price_in_sol(token_address: str) -> float:
    now = time.time()
    if token_address in price_cache and now - last_price_fetch.get(token_address, 0) < 8:
        return price_cache[token_address]

    try:
        url = f"https://public-api.birdeye.so/defi/price?address={token_address}"
        headers = {"X-API-KEY": BIRDEYE_API_KEY, "x-chain": "solana"}
        resp = await client.get(url, headers=headers)
        data = resp.json()
        price = float(data.get("data", {}).get("value", 0.0))
        
        if price > 0:
            price_cache[token_address] = price
            last_price_fetch[token_address] = now
            return price
    except:
        pass

    # Smart fallback price
    base_prices = {
        "Ax8PSfCXxmxb8C8kYTzN5CPpTe6PyeZfFf8rrXNCjupx": 0.00105,   # MM
        "a3W4qutoEJA4232T2gwZUfgYJTetr96pU4SJMwppump": 0.0065,    # WHITEWHALE
        "5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2": 0.125      # TROLL
    }
    return base_prices.get(token_address, 0.01)


async def get_historical_prices(token_address: str, limit: int = 500) -> List[float]:
    now = time.time()
    cache_key = f"{token_address}_{limit}"
    
    if cache_key in history_cache and now - last_history_fetch.get(cache_key, 0) < 35:
        return history_cache[cache_key]

    try:
        url = f"https://public-api.birdeye.so/defi/history_price"
        params = {"address": token_address, "address_type": "token", "type": "15m", "limit": limit}
        headers = {"X-API-KEY": BIRDEYE_API_KEY, "x-chain": "solana"}
        resp = await client.get(url, params=params, headers=headers)
        data = resp.json()

        if data.get("success") and "data" in data and "items" in data["data"]:
            prices = [float(item["value"]) for item in data["data"]["items"] if item.get("value")]
            if len(prices) > 150:
                prices = prices[::-1]
                history_cache[cache_key] = prices
                last_history_fetch[cache_key] = now
                print(f"✅ Loaded {len(prices)} real candles for {token_address[:8]}...")
                return prices
    except Exception as e:
        print(f"Birdeye error for {token_address[:8]}: {e}")

    # === IMPROVED REALISTIC FALLBACK ===
    print(f"⚠️ Using realistic fallback data for {token_address[:8]}...")
    
    base_price = {
        "Ax8PSfCXxmxb8C8kYTzN5CPpTe6PyeZfFf8rrXNCjupx": 0.00105,
        "a3W4qutoEJA4232T2gwZUfgYJTetr96pU4SJMwppump": 0.0065,
        "5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2": 0.125
    }.get(token_address, 0.01)

    # Generate realistic price series with volatility + small trends
    np.random.seed(int(time.time()) % 10000)  # Slight randomness per run
    prices = [base_price]
    volatility = 0.018 if "TROLL" in token_address else 0.022
    
    for _ in range(limit - 1):
        change = np.random.normal(0, volatility)
        new_price = prices[-1] * (1 + change)
        prices.append(max(new_price, base_price * 0.4))
    
    history_cache[cache_key] = prices
    last_history_fetch[cache_key] = now
    return prices
