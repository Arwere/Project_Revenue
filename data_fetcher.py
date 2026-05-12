import asyncio
import time
from typing import Dict, List, Optional
import httpx
from datetime import datetime
from config import config

client = httpx.AsyncClient(timeout=15.0)

async def http_get_json(url: str, params: dict = None):
    try:
        resp = await client.get(url, params=params, headers={"user-agent": "solana-trading-agent/2.0"})
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}

async def get_token_metadata(token_address: str) -> Dict:
    try:
        data = await http_get_json("https://lite-api.jup.ag/tokens/v2/search", {"query": token_address})
        if isinstance(data, list) and data:
            for token in data:
                if token.get("id") == token_address:
                    return token
            return data[0]
        return data if isinstance(data, dict) else {}
    except:
        return {}

async def get_price_in_sol(token_address: str) -> float:
    try:
        quote = await http_get_json("https://api.jup.ag/swap/v1/quote", {
            "inputMint": token_address,
            "outputMint": "So11111111111111111111111111111111111111112",
            "amount": "1000000000",
            "slippageBps": 50,
        })
        return int(quote.get("outAmount", 0)) / 1_000_000_000
    except:
        return 0.0

async def get_usd_price(token_address: str) -> Optional[float]:
    try:
        data = await http_get_json("https://lite-api.jup.ag/price/v3", {"ids": token_address})
        return data.get(token_address, {}).get("usdPrice")
    except:
        return None

async def get_historical_prices(token_address: str, limit: int = 800) -> List[float]:
    """Try to get real history (Birdeye fallback possible later)"""
    try:
        current = await get_price_in_sol(token_address)
        # For now return recent prices (will improve with Birdeye API key)
        return [current * (1 + i*0.0005) for i in range(-limit, 1)]  # Placeholder realistic series
    except:
        return [0.001] * 100

async def get_full_market_data(token_address: str) -> Dict:
    meta = await get_token_metadata(token_address)
    price_sol, usd = await asyncio.gather(
        get_price_in_sol(token_address),
        get_usd_price(token_address)
    )
    
    return {
        "price_sol": price_sol,
        "usd_price": usd,
        "market_cap": meta.get("mc") or meta.get("marketCap"),
        "volume": meta.get("v24h") or 0,
        "symbol": meta.get("symbol"),
        "name": meta.get("name"),
        "timestamp": datetime.now().isoformat()
    }
