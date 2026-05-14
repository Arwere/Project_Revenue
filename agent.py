from typing import Dict, List
from config import config
from strategies import TrendStrategy, MomentumStrategy, MeanReversionStrategy, VolatilityStrategy
from risk_manager import RiskManager

class TradingAgent:
    def __init__(self):
        self.strategies = {
            "trend": TrendStrategy(),
            "momentum": MomentumStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "volatility": VolatilityStrategy()
        }
        self.risk_manager = RiskManager()

    def get_risk_adjusted_decision(self, token_config, market_data: Dict, prices: List[float], bot_name: str = None) -> Dict:
        if len(prices) < 100:
            return {"action": "HOLD", "final_score": 5.0}

        # Multi-timeframe analysis
        tf_scores = []
        # Current (15m)
        tf_scores.append(self._analyze_tf(prices[-400:], "15m"))
        # 1h (resampled)
        if len(prices) > 60:
            tf_scores.append(self._analyze_tf(prices[-300::4], "1h"))
        # 4h
        if len(prices) > 200:
            tf_scores.append(self._analyze_tf(prices[-200::16], "4h"))

        final_score = sum(tf_scores) / len(tf_scores)

        if final_score >= 7.8:
            action = "STRONG_BUY"
        elif final_score >= 6.8:
            action = "BUY"
        elif final_score <= 4.5:
            action = "SELL"
        else:
            action = "HOLD"

        return {
            "action": action,
            "final_score": round(final_score, 1),
            "suggested_capital_percent": 0.30 if action in ["BUY", "STRONG_BUY"] else 0.0,
            "tp": 0.15,
            "sl": -0.08,
            "bot_name": bot_name
        }

    def _analyze_tf(self, prices: List[float], tf: str):
        total = 0.0
        for strategy in self.strategies.values():
            result = strategy.analyze(prices, None, None)
            total += result.get("score", 5.0)
        return total / len(self.strategies)
