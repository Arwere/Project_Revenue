from typing import Dict, List
from config import config
from strategies import TrendStrategy, MomentumStrategy, MeanReversionStrategy, VolatilityStrategy
from risk_manager import RiskManager

class Poseidon:
    def __init__(self):
        self.strategies = {
            "trend": TrendStrategy(),
            "momentum": MomentumStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "volatility": VolatilityStrategy()
        }
        self.risk_manager = RiskManager()

    async def get_risk_adjusted_decision(self, token_config, market_data: Dict, prices: List[float], bot_name: str = None) -> Dict:
        """
        Main decision engine with multi-timeframe weighting + conservative risk.
        """
        if len(prices) < 100:
            return {
                "action": "HOLD",
                "final_score": 5.0,
                "suggested_capital_percent": 0.0,
                "tp": 0.0,
                "sl": 0.0,
                "reason": "Insufficient data"
            }

        # === Multi-Timeframe Weighted Analysis ===
        tf_weights = {
            "5m":  0.40,
            "30m": 0.25,
            "1h":  0.18,
            "4h":  0.10,
            "1d":  0.05,
            "1w":  0.02
        }

        tf_scores = []

        # 5m (most recent data)
        tf_scores.append(self._analyze_tf(prices[-400:], tf_weights["5m"]))

        # 30m
        if len(prices) > 30:
            tf_scores.append(self._analyze_tf(prices[-300::6], tf_weights["30m"]))

        # 1h
        if len(prices) > 60:
            tf_scores.append(self._analyze_tf(prices[-240::12], tf_weights["1h"]))

        # 4h
        if len(prices) > 200:
            tf_scores.append(self._analyze_tf(prices[-200::48], tf_weights["4h"]))

        # 1d
        if len(prices) > 400:
            tf_scores.append(self._analyze_tf(prices[-150::192], tf_weights["1d"]))

        final_score = sum(tf_scores)

        # === Decision Logic ===
        if final_score >= 7.8:
            action = "STRONG_BUY"
        elif final_score >= 6.7:
            action = "BUY"
        elif final_score <= 4.5:
            action = "SELL"
        else:
            action = "HOLD"

        # === Conservative Capital Allocation ===
        capital_percent = self.risk_manager.get_conservative_position_size(
            final_score, market_data.get("price_sol", 0), token_config
        )

        return {
            "action": action,
            "final_score": round(final_score, 1),
            "suggested_capital_percent": round(capital_percent, 3),
            "tp": 0.145,          # 14.5% take profit
            "sl": -0.072,         # -7.2% stop loss
            "bot_name": bot_name,
            "reason": "Multi-Timeframe Weighted + Risk Adjusted"
        }

    def _analyze_tf(self, prices: List[float], weight: float = 1.0) -> float:
        """Analyze one timeframe and return weighted score"""
        if len(prices) < 30:
            return 5.0 * weight

        total = 0.0
        for strategy in self.strategies.values():
            result = strategy.analyze(prices)
            total += result.get("score", 5.0)

        avg_score = total / len(self.strategies)
        return avg_score * weight
