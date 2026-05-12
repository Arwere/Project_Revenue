from typing import Dict, List
from indicators import get_all_indicators
from config import config

def get_indicators_on_tf(prices: List[float], tf_key: str, token_config=None):
    """Get indicators using strategy-specific timeframe"""
    if token_config and hasattr(token_config, 'timeframes') and token_config.timeframes:
        tf = token_config.timeframes.get(tf_key, config.TIMEFRAMES.get(tf_key, 50))
    else:
        tf = config.TIMEFRAMES.get(tf_key, 50)
    
    recent_prices = prices[-tf:] if len(prices) >= tf else prices
    return get_all_indicators(recent_prices)


class TrendStrategy:
    def analyze(self, prices: List[float], market_data: Dict = None, token_config=None):
        ind = get_indicators_on_tf(prices, "trend", token_config)
        score = ind.get("confluence_score", 5.0)
        reason = "Neutral trend"

        price_vs_sma = ind.get("price_vs_sma20", 0)
        macd_hist = ind.get("macd_histogram")

        if macd_hist and macd_hist > 0 and price_vs_sma > -1.5:
            score += 2.5
            reason = "Strong uptrend with positive MACD"
        elif price_vs_sma < -3.0:
            score += 1.8
            reason = "Dip in potential uptrend"

        return {
            "name": "Trend",
            "score": round(min(10.0, max(0.0, score)), 1),
            "recommendation": "BULLISH" if score >= 7 else "NEUTRAL",
            "reason": reason,
            "indicators": ind
        }


class MomentumStrategy:
    def analyze(self, prices: List[float], market_data: Dict = None, token_config=None):
        ind = get_indicators_on_tf(prices, "momentum", token_config)
        score = ind.get("confluence_score", 5.0)
        reason = "No strong momentum"

        rsi = ind.get("rsi")
        if rsi and rsi < 32:
            score += 3.2
            reason = "Deeply oversold RSI"
        elif rsi and rsi < 40:
            score += 1.5
            reason = "Oversold conditions"

        return {
            "name": "Momentum",
            "score": round(min(10.0, max(0.0, score)), 1),
            "recommendation": "BUY" if score >= 7 else "NEUTRAL",
            "reason": reason,
            "indicators": ind
        }


class MeanReversionStrategy:
    def analyze(self, prices: List[float], market_data: Dict = None, token_config=None):
        ind = get_indicators_on_tf(prices, "mean_reversion", token_config)
        score = ind.get("confluence_score", 5.0)
        reason = "No clear reversion"

        current = ind.get("current_price", 0)
        bb_lower = ind.get("bollinger_lower")
        if bb_lower and current < bb_lower * 1.025:
            score += 3.5
            reason = "Strong dip at lower Bollinger Band"

        return {
            "name": "MeanReversion",
            "score": round(min(10.0, max(0.0, score)), 1),
            "recommendation": "BUY" if score >= 7 else "NEUTRAL",
            "reason": reason,
            "indicators": ind
        }


class VolatilityStrategy:
    def analyze(self, prices: List[float], market_data: Dict = None, token_config=None):
        ind = get_indicators_on_tf(prices, "volatility", token_config)
        score = ind.get("confluence_score", 5.0)
        reason = "Normal volatility"

        vol = ind.get("volatility_percent", 0)
        if vol > 10 and ind.get("price_vs_sma20", 0) < -2.5:
            score += 3.0
            reason = "High volatility dip opportunity"

        return {
            "name": "Volatility",
            "score": round(min(10.0, max(0.0, score)), 1),
            "recommendation": "BUY" if score >= 7 else "NEUTRAL",
            "reason": reason,
            "indicators": ind
        }
