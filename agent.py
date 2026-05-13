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

    def get_risk_adjusted_decision(self, token_config, market_data: Dict, prices: List[float]) -> Dict:
        if len(prices) < 100:
            return {"recommendation": "MONITOR", "final_score": 5.0, "action": "HOLD"}

        results = {}
        weighted_score = 0.0

        for name, strategy in self.strategies.items():
            result = strategy.analyze(prices, market_data, token_config)
            results[name] = result
            weighted_score += result.get("score", 5.0) * 0.25

        final_score = weighted_score

        # === VERY AGGRESSIVE FOR TESTING ===
        if final_score >= 5.0:        # Almost always buy
            action = "BUY"
            rec = "BUY"
        else:
            action = "HOLD"
            rec = "MONITOR"

        decision = {
            "recommendation": rec,
            "final_score": round(final_score, 2),
            "action": action,
            "stack_results": results,
            "reasoning": ["Test mode - aggressive"]
        }

        risk_info = self.risk_manager.get_trade_recommendation(decision, market_data.get("price_sol", 0), token_config)
        decision["action"] = risk_info.get("action", action)

        return decision
