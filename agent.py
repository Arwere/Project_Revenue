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
        self.use_claude = True   # Toggle this to False for pure rules

    async def get_risk_adjusted_decision(self, token_config, market_data: Dict, prices: List[float], bot_name: str = None) -> Dict:
        if len(prices) < 80:
            return {"action": "HOLD", "final_score": 5.0, "suggested_capital_percent": 0.0, "reason": "Not enough data"}

        # 1. Technical Analysis Score
        technical_score = self._calculate_multi_tf_score(prices)

        # 2. Claude Decision Layer
        if self.use_claude:
            context = self._build_claude_context(token_config, market_data, prices, technical_score)
            claude_result = await claude.get_decision(context)

            final_score = round((technical_score * 0.55) + (claude_result.get("final_score", 5.5) * 0.45), 1)

            decision = {
                "action": claude_result.get("action", "HOLD"),
                "final_score": final_score,
                "suggested_capital_percent": claude_result.get("suggested_capital_percent", 0.12),
                "tp": claude_result.get("tp", 0.14),
                "sl": claude_result.get("sl", -0.07),
                "bot_name": bot_name,
                "reason": claude_result.get("reason", "Hybrid Analysis")
            }
        else:
            # Pure rules fallback
            decision = {
                "action": "BUY" if technical_score >= 6.8 else "HOLD",
                "final_score": round(technical_score, 1),
                "suggested_capital_percent": self.risk_manager.get_conservative_position_size(technical_score, market_data.get("price_sol", 0), token_config),
                "tp": 0.14,
                "sl": -0.07,
                "bot_name": bot_name,
                "reason": "Technical Rules Only"
            }

        return decision

    def _calculate_multi_tf_score(self, prices: List[float]) -> float:
        weights = [0.40, 0.25, 0.18, 0.10, 0.05, 0.02]
        tf_data = [
            prices[-400:],
            prices[-300::6] if len(prices) > 30 else prices[-100:],
            prices[-240::12] if len(prices) > 60 else prices[-80:],
            prices[-200::48] if len(prices) > 200 else prices[-60:],
        ]

        score = 0.0
        for data, weight in zip(tf_data, weights):
            score += self._analyze_single_tf(data) * weight
        return score

    def _analyze_single_tf(self, prices: List[float]) -> float:
        if len(prices) < 30:
            return 5.0
        total = 0.0
        for strat in self.strategies.values():
            total += strat.analyze(prices).get("score", 5.0)
        return total / len(self.strategies)

    def _build_claude_context(self, token_config, market_data, prices, technical_score):
        price = market_data.get("price_sol", 0)
        trend = "Rising" if prices[-1] > prices[-30] else "Falling" if prices[-1] < prices[-30] else "Sideways"
        return f"Token: {token_config.symbol}\nPrice: {price:.8f} SOL\nTechnical Score: {technical_score:.1f}\nTrend: {trend}\nMake a trading decision."
