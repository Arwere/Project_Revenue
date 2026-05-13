from typing import Dict, List, Any
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
            return {"action": "HOLD", "final_score": 5.0, "suggested_capital_percent": 0.0}

        total_score = 0.0
        for strategy in self.strategies.values():
            result = strategy.analyze(prices, market_data, token_config)
            total_score += result.get("score", 5.0)

        final_score = total_score / len(self.strategies)
        final_score = min(final_score + 1.3, 9.8)   # Real data boost

        if final_score >= 7.8:
            action = "STRONG_BUY"
        elif final_score >= 6.8:
            action = "BUY"
        elif final_score <= 4.2:
            action = "SELL"
        else:
            action = "HOLD"

        decision = {
            "action": action,
            "final_score": round(final_score, 1),
            "suggested_capital_percent": 0.35 if action in ["BUY", "STRONG_BUY"] else 0.0,
            "tp": 0.145,
            "sl": -0.085,
            "bot_name": bot_name,
            "reason": "Multi-strategy confluence"
        }

        return decision
