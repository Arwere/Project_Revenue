from typing import Dict, List
from config import config
from strategies import TrendStrategy, MomentumStrategy, MeanReversionStrategy, VolatilityStrategy
from risk_manager import RiskManager
from claude_brain import claude

class Poseidon:
    def __init__(self):
        self.strategies = {
            "trend": TrendStrategy(),
            "momentum": MomentumStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "volatility": VolatilityStrategy()
        }
        self.risk_manager = RiskManager()
        self.use_claude = True   # Set to False to disable Claude

    async def get_risk_adjusted_decision(self, token_config, market_data: Dict, prices: List[float], bot_name: str = None) -> Dict:
        if len(prices) < 100:
            return {"action": "HOLD", "final_score": 5.0, "suggested_capital_percent": 0.0}

        # Technical Analysis
        total_score = 0.0
        for strategy in self.strategies.values():
            result = strategy.analyze(prices, market_data, token_config)
            total_score += result.get("score", 5.0)

        tech_score = total_score / len(self.strategies)
        tech_score = min(tech_score + 1.2, 9.8)

        # Claude Decision (Hybrid)
        if self.use_claude:
            context = {
                "symbol": token_config.symbol,
                "price": market_data.get("price_sol", 0),
                "tech_score": tech_score,
                "price_trend": "Up" if prices[-1] > prices[-20] else "Down" if prices[-1] < prices[-20] else "Sideways",
                "rsi": "N/A",
                "macd_hist": "N/A"
            }
            claude_decision = await claude.get_decision(context)
            final_action = claude_decision.get("action", "HOLD")
            confidence = claude_decision.get("confidence", 0.5)
        else:
            final_action = "BUY" if tech_score >= 7.0 else "HOLD"
            confidence = tech_score / 10.0

        return {
            "action": final_action,
            "final_score": round(tech_score, 1),
            "suggested_capital_percent": claude_decision.get("suggested_capital_percent", 0.25) if self.use_claude else 0.30,
            "confidence": confidence,
            "reason": claude_decision.get("reason", "Technical confluence") if self.use_claude else "Rule-based"
        }
