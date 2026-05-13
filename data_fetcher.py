import asyncio
import numpy as np
from typing import List, Dict
import httpx
from datetime import datetime, timedelta
from config import config

client = httpx.AsyncClient(timeout=20.0)
BIRDEYE_API_KEY = "fc1e63ea2f2548ebb120f97580d51923"

async def get_historical_prices(token_address: str, limit: int = 1000) -> List[float]:
    """Real historical prices from Birdeye (15m candles)"""
    print(f"📡 Fetching real data for {token_address}...")

    # Try last 30-60 days
    time_to = int(datetime.now().timestamp())
    time_from = int((datetime.now() - timedelta(days=45)).timestamp())

    url = f"https://public-api.birdeye.so/defi/history_price"
    params = {
        "address": token_address,
        "address_type": "token",
        "type": "15m",
        "time_from": time_from,
        "time_to": time_to
    }
    headers = {
        "X-API-KEY": BIRDEYE_API_KEY,
        "x-chain": "solana",
        "accept": "application/json"
    }

    try:
        resp = await client.get(url, params=params, headers=headers)
        data = resp.json()

        if data.get("success") and "data" in data and "items" in data["data"]:
            items = data["data"]["items"]
            prices = [float(item["value"]) for item in items if item.get("value")]
            if len(prices) >= 300:
                prices = prices[::-1]  # oldest -> newest
                print(f"✅ Loaded {len(prices)} real candles")
                return prices
    except Exception as e:
        print(f"⚠️ Birdeye fetch failed: {e}")

    # Safe fallback (very rare now)
    print("⚠️ Using minimal fallback")
    return [0.0025] * limit

# Keep your existing get_price_in_sol if needed
async def get_price_in_sol(token_address: str) -> float:
    try:
        url = f"https://public-api.birdeye.so/defi/price?address={token_address}"
        headers = {"X-API-KEY": BIRDEYE_API_KEY, "x-chain": "solana"}
        resp = await client.get(url, headers=headers)
        data = resp.json()
        return float(data.get("data", {}).get("value", 0.0))
    except:
        return 0.0
