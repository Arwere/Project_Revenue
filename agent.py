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
            return {"action": "HOLD", "final_score": 5.0}

        total_score = 0.0
        details = {}

        for name, strategy in self.strategies.items():
            result = strategy.analyze(prices, market_data, token_config)
            score = result.get("score", 5.0)
            details[name] = score
            total_score += score

        final_score = total_score / len(self.strategies)
        final_score = min(final_score + 1.4, 9.8)   # Stronger boost for real data

        if final_score >= 7.4:
            action = "STRONG_BUY"
        elif final_score >= 6.8:
            action = "BUY"
        else:
            action = "HOLD"

        decision = {
            "action": action,
            "final_score": round(final_score, 1),
            "strategy_details": details
        }

        # Light risk filter
        risk_info = self.risk_manager.get_trade_recommendation(decision, market_data.get("price_sol", 0), token_config)
        if risk_info.get("action") != "BLOCK":
            decision["action"] = action

        return decision
