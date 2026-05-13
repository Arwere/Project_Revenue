from typing import Dict, List
from indicators import get_all_indicators
from config import config


def get_indicators_on_tf(prices: List[float], tf_key: str, token_config=None):
    tf_map = {"trend": 100, "momentum": 50, "mean_reversion": 40, "volatility": 60}
    tf = tf_map.get(tf_key, 60)
    if token_config and hasattr(token_config, 'timeframes'):
        tf = token_config.timeframes.get(tf_key, tf)
    
    recent = prices[-tf:] if len(prices) >= tf else prices
    return get_all_indicators(recent)


class TrendStrategy:
    def analyze(self, prices: List[float], market_data: Dict = None, token_config=None):
        ind = get_indicators_on_tf(prices, "trend", token_config)
        score = 5.0

        if ind.get("price_vs_sma20", 0) > 1.8 and ind.get("macd_histogram", 0) > 0:
            score += 3.2
        elif ind.get("price_vs_sma20", 0) > 0.8:
            score += 1.5

        return {
            "name": "Trend",
            "score": round(min(10.0, max(2.0, score)), 1),
            "recommendation": "BULLISH" if score >= 7.5 else "NEUTRAL",
            "reason": "Uptrend detected" if score >= 7.5 else "Neutral trend"
        }


class MomentumStrategy:
    def analyze(self, prices: List[float], market_data: Dict = None, token_config=None):
        ind = get_indicators_on_tf(prices, "momentum", token_config)
        score = 5.0
        rsi = ind.get("rsi", 50)

        if rsi < 33:
            score += 3.8
        elif rsi < 40:
            score += 2.0

        return {
            "name": "Momentum",
            "score": round(min(10.0, max(2.0, score)), 1),
            "recommendation": "BUY" if score >= 7.5 else "NEUTRAL",
            "reason": f"Oversold (RSI {rsi:.1f})" if rsi < 40 else "No momentum"
        }


class MeanReversionStrategy:
    def analyze(self, prices: List[float], market_data: Dict = None, token_config=None):
        ind = get_indicators_on_tf(prices, "mean_reversion", token_config)
        score = 5.0

        if ind.get("price_vs_sma20", 0) < -2.5:
            score += 3.5

        return {
            "name": "MeanReversion",
            "score": round(min(10.0, max(2.0, score)), 1),
            "recommendation": "BUY" if score >= 7.8 else "NEUTRAL",
            "reason": "Dip detected" if score >= 7.8 else "No reversion"
        }


class VolatilityStrategy:
    def analyze(self, prices: List[float], market_data: Dict = None, token_config=None):
        ind = get_indicators_on_tf(prices, "volatility", token_config)
        score = 5.0

        if ind.get("volatility_percent", 0) > 9 and ind.get("price_vs_sma20", 0) < -2.0:
            score += 3.2

        return {
            "name": "Volatility",
            "score": round(min(10.0, max(2.0, score)), 1),
            "recommendation": "BUY" if score >= 7.7 else "NEUTRAL",
            "reason": "Volatility dip" if score >= 7.7 else "Normal vol"
        }
