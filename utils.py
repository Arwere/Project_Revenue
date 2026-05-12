import urllib.request
import urllib.parse
import json
from config import TOKEN_ADDRESS

def http_get_json(url: str, params: dict = None, timeout: int = 15):
    try:
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        request = urllib.request.Request(url, headers={
            "accept": "application/json",
            "user-agent": "solana-agent/2.0"
        })
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except:
        return {}

def get_token_metadata():
    try:
        data = http_get_json("https://lite-api.jup.ag/tokens/v2/search", {"query": TOKEN_ADDRESS})
        if isinstance(data, list) and data:
            for token in data:
                if token.get("id") == TOKEN_ADDRESS:
                    return token
            return data[0]
        return data if isinstance(data, dict) else {}
    except:
        return {}

def get_price_in_sol() -> float:
    try:
        quote = http_get_json("https://api.jup.ag/swap/v1/quote", {
            "inputMint": TOKEN_ADDRESS,
            "outputMint": "So11111111111111111111111111111111111111112",
            "amount": "1000000000",
            "slippageBps": 50,
        })
        return int(quote.get("outAmount", 0)) / 1_000_000_000
    except:
        return 0.0

def get_usd_price():
    try:
        data = http_get_json("https://lite-api.jup.ag/price/v3", {"ids": TOKEN_ADDRESS})
        return data.get(TOKEN_ADDRESS, {}).get("usdPrice")
    except:
        return None

def get_market_cap(token_metadata: dict):
    try:
        return token_metadata.get("mcap") or token_metadata.get("marketCap")
    except:
        return None

def get_24h_volume(token_metadata: dict) -> float:
    try:
        stats = token_metadata.get("stats24h") or {}
        return float(stats.get("buyVolume") or 0) + float(stats.get("sellVolume") or 0)
    except:
        return 0.0