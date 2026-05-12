import statistics
from typing import Dict, List, Tuple

def calculate_ema(prices: List[float], period: int):
    if len(prices) < period:
        return None
    k = 2 / (period + 1)
    ema = statistics.mean(prices[:period])
    for price in prices[period:]:
        ema = price * k + ema * (1 - k)
    return ema

def calculate_rsi(prices: List[float], period: int = 14):
    if len(prices) <= period:
        return None
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [max(d, 0) for d in deltas[-period:]]
    losses = [abs(min(d, 0)) for d in deltas[-period:]]
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period if sum(losses) > 0 else 0.0001

    for g, l in zip(gains, losses):
        avg_gain = (avg_gain * (period - 1) + g) / period
        avg_loss = (avg_loss * (period - 1) + l) / period

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices: List[float]):
    if len(prices) < 40:
        return None, None, None
    ema12 = calculate_ema(prices, 12)
    ema26 = calculate_ema(prices, 26)
    if not ema12 or not ema26:
        return None, None, None
    macd_line = ema12 - ema26
    signal = calculate_ema([macd_line] * 9, 9) or macd_line
    histogram = macd_line - signal
    return macd_line, signal, histogram

def calculate_bollinger_bands(prices: List[float], period: int = 20, std_mult: float = 2.0):
    if len(prices) < period:
        return None, None, None
    sma = statistics.mean(prices[-period:])
    std = statistics.stdev(prices[-period:]) if len(prices[-period:]) > 1 else 0
    upper = sma + std * std_mult
    lower = sma - std * std_mult
    return sma, upper, lower

def calculate_atr(prices: List[float], period: int = 14):
    if len(prices) < period + 1:
        return None
    trs = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
    return statistics.mean(trs[-period:])

def get_all_indicators(prices: List[float]) -> Dict:
    if len(prices) < 20:
        return {"current_price": prices[-1] if prices else 0, "data_points": len(prices), "confluence_score": 0}

    current = prices[-1]
    data_points = len(prices)

    sma20 = statistics.mean(prices[-20:]) if data_points >= 20 else None
    rsi = calculate_rsi(prices)
    macd_line, _, macd_hist = calculate_macd(prices)
    bb_mid, bb_upper, bb_lower = calculate_bollinger_bands(prices)
    atr = calculate_atr(prices)

    price_vs_sma20 = ((current - sma20) / sma20 * 100) if sma20 else 0
    bb_position = (current - bb_lower) / (bb_upper - bb_lower) if bb_upper and bb_lower and bb_upper != bb_lower else 0.5
    volatility = (atr / current * 100) if atr and current > 0 else 0

    # Advanced Confluence Scoring (Strategy-agnostic base)
    confluence = 5.0

    # Strong Dips
    if price_vs_sma20 < -3.0: confluence += 3.5
    elif price_vs_sma20 < -1.8: confluence += 2.0

    # Oversold Momentum
    if rsi and rsi < 32: confluence += 3.5
    elif rsi and rsi < 40: confluence += 1.5
    if rsi and rsi > 72: confluence -= 2.5

    # MACD Trend Reversal
    if macd_hist and macd_hist > 0.000001: confluence += 2.2
    if macd_hist and macd_hist < -0.000001 and price_vs_sma20 < -2: confluence += 1.8  # Bullish divergence on dip

    # Bollinger Bands
    if bb_lower and current < bb_lower * 1.02: confluence += 3.0   # Strong lower band touch (dip)
    if bb_position < 0.15: confluence += 2.0

    # Volatility & Data Quality
    if volatility > 8: confluence += 1.0   # High volatility = opportunity
    if data_points > 100: confluence += 1.0

    confluence = max(0, min(10, confluence))

    return {
        "current_price": current,
        "sma20": sma20,
        "rsi": rsi,
        "macd_histogram": macd_hist,
        "bollinger_lower": bb_lower,
        "bollinger_mid": bb_mid,
        "bollinger_upper": bb_upper,
        "bb_position": round(bb_position, 2),
        "atr": atr,
        "volatility_percent": round(volatility, 2),
        "price_vs_sma20": round(price_vs_sma20, 2),
        "confluence_score": round(confluence, 1),
        "data_points": data_points
    }