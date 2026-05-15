import numpy as np
import pandas as pd
from typing import List, Dict

def get_indicators_on_tf(prices: List[float]):
    if len(prices) < 50:
        return {"rsi": 50, "price_vs_sma20": 0, "macd_hist": 0, "volatility": 10.0, "sma50": prices[-1] if prices else 0}

    prices = np.array(prices)
    delta = np.diff(prices)
    gain = np.maximum(delta, 0)
    loss = np.abs(np.minimum(delta, 0))
    
    avg_gain = pd.Series(gain).rolling(14).mean().iloc[-1]
    avg_loss = pd.Series(loss).rolling(14).mean().iloc[-1]
    rs = avg_gain / avg_loss if avg_loss > 0 else 100
    rsi = 100 - (100 / (1 + rs))

    sma20 = np.mean(prices[-20:])
    sma50 = np.mean(prices[-50:]) if len(prices) >= 50 else sma20
    price_vs_sma20 = (prices[-1] - sma20) / sma20 * 100

    ema12 = pd.Series(prices).ewm(span=12, adjust=False).mean().iloc[-1]
    ema26 = pd.Series(prices).ewm(span=26, adjust=False).mean().iloc[-1]
    macd = ema12 - ema26
    signal = pd.Series(prices).ewm(span=9, adjust=False).mean().iloc[-1]
    macd_hist = macd - signal

    volatility = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100 if len(prices) > 20 else 10.0

    return {
        "rsi": rsi,
        "price_vs_sma20": price_vs_sma20,
        "macd_hist": macd_hist,
        "volatility": volatility,
        "sma50": sma50
    }


class MeanReversionStrategy:
    def analyze(self, prices: List[float], market_data=None, token_config=None):
        ind = get_indicators_on_tf(prices)
        score = 5.0
        if ind["price_vs_sma20"] < -5.0 and ind["rsi"] < 38:
            score += 4.5
        elif ind["price_vs_sma20"] < -3.0 and ind["rsi"] < 44:
            score += 3.0
        if ind["macd_hist"] > 0:
            score += 1.4
        return {"score": min(score, 9.9), "reason": "Mean Reversion"}


class TrendStrategy:
    def analyze(self, prices: List[float], market_data=None, token_config=None):
        ind = get_indicators_on_tf(prices)
        score = 5.0
        if ind["price_vs_sma20"] > 2.0 and ind["rsi"] > 52:
            score += 3.2
        return {"score": score, "reason": "Trend"}


class MomentumStrategy:
    def analyze(self, prices: List[float], market_data=None, token_config=None):
        ind = get_indicators_on_tf(prices)
        score = 5.0
        if ind["rsi"] > 60:
            score += 3.3
        return {"score": score, "reason": "Momentum"}


class VolatilityStrategy:
    def analyze(self, prices: List[float], market_data=None, token_config=None):
        ind = get_indicators_on_tf(prices)
        score = 5.0
        if ind["volatility"] > 7.5:
            score += 2.6
        return {"score": score, "reason": "Volatility"}


def get_all_strategy_results(prices: List[float], market_data=None, token_config=None):
    strategies = [MeanReversionStrategy(), TrendStrategy(), MomentumStrategy(), VolatilityStrategy()]
    total = sum(s.analyze(prices).get("score", 5.0) for s in strategies)
    return {"final_score": round(total / 4, 1)}
