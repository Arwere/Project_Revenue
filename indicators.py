import numpy as np
from typing import Dict, List


def get_all_indicators(prices: List[float]) -> Dict:
    if len(prices) < 30:
        return {"confluence_score": 5.0, "rsi": 50.0}

    prices = np.array(prices, dtype=float)
    current = prices[-1]

    # SMA
    sma20 = np.mean(prices[-20:])

    # RSI - Safe version
    delta = np.diff(prices)
    gain = np.maximum(delta, 0)
    loss = np.abs(np.minimum(delta, 0))
    
    avg_gain = np.mean(gain[-14:]) if len(gain) >= 14 else 0
    avg_loss = np.mean(loss[-14:]) if len(loss) >= 14 else 0.0001
    
    rsi = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_gain + avg_loss > 0 else 50

    # MACD
    macd_histogram = np.mean(prices[-12:]) - np.mean(prices[-26:]) if len(prices) >= 26 else 0

    # Volatility
    returns = np.diff(prices) / np.maximum(prices[:-1], 0.000001)
    volatility = np.std(returns[-20:]) * 100 if len(returns) > 20 else 0

    # Score
    score = 5.0
    if current > sma20 and macd_histogram > 0:
        score += 2.8
    if rsi < 40:
        score += 3.0
    if volatility > 8:
        score += 1.5

    return {
        "rsi": round(float(rsi), 2),
        "macd_histogram": round(float(macd_histogram), 4),
        "price_vs_sma20": round((current - sma20) / sma20 * 100, 2),
        "volatility_percent": round(float(volatility), 2),
        "confluence_score": round(min(10.0, max(2.0, score)), 1)
    }
