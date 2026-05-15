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
        self.use_claude = True   # Set to False if you want pure rules

    async def get_risk_adjusted_decision(self, token_config, market_data: Dict, prices: List[float], bot_name: str = None) -> Dict:
        if len(prices) < 100:
            return {"action": "HOLD", "final_score": 5.0, "suggested_capital_percent": 0.0, "reason": "Insufficient data"}

        # Step 1: Rule-based Technical Score
        tf_score = self._calculate_multi_tf_score(prices)

        # Step 2: Claude Final Decision (Hybrid)
        if self.use_claude:
            context = self._build_claude_context(token_config, market_data, prices, tf_score)
            claude_decision = await claude.get_decision(context)
            
            # Blend rule score with Claude
            final_score = (tf_score * 0.6) + (claude_decision.get("final_score", 5.0) * 0.4)
            
            decision = {
                "action": claude_decision.get("action", "HOLD"),
                "final_score": round(final_score, 1),
                "suggested_capital_percent": claude_decision.get("suggested_capital_percent", 0.0),
                "tp": claude_decision.get("tp", 0.14),
                "sl": claude_decision.get("sl", -0.07),
                "bot_name": bot_name,
                "reason": claude_decision.get("reason", "Hybrid Decision")
            }
        else:
            # Pure rule-based fallback
            decision = {
                "action": "BUY" if tf_score >= 6.8 else "HOLD",
                "final_score": round(tf_score, 1),
                "suggested_capital_percent": self.risk_manager.get_conservative_position_size(tf_score, market_data.get("price_sol", 0), token_config),
                "tp": 0.145,
                "sl": -0.072,
                "bot_name": bot_name,
                "reason": "Pure Technical Rules"
            }

        return decision

    def _calculate_multi_tf_score(self, prices: List[float]) -> float:
        tf_weights = {"5m": 0.40, "30m": 0.25, "1h": 0.18, "4h": 0.10, "1d": 0.05, "1w": 0.02}
        tf_scores = []

        tf_scores.append(self._analyze_tf(prices[-400:], tf_weights["5m"]))
        if len(prices) > 30: tf_scores.append(self._analyze_tf(prices[-300::6], tf_weights["30m"]))
        if len(prices) > 60: tf_scores.append(self._analyze_tf(prices[-240::12], tf_weights["1h"]))
        if len(prices) > 200: tf_scores.append(self._analyze_tf(prices[-200::48], tf_weights["4h"]))

        return sum(tf_scores)

    def _analyze_tf(self, prices: List[float], weight: float) -> float:
        if len(prices) < 30:
            return 5.0 * weight
        total = 0.0
        for strategy in self.strategies.values():
            result = strategy.analyze(prices)
            total += result.get("score", 5.0)
        return (total / len(self.strategies)) * weight

    def _build_claude_context(self, token_config, market_data, prices, technical_score):
        current_price = market_data.get("price_sol", 0)
        return f"""
Token: {token_config.symbol}
Current Price: {current_price}
Technical Score: {technical_score:.1f}
Recent Price Trend: {'Up' if prices[-1] > prices[-50] else 'Down' if prices[-1] < prices[-50] else 'Sideways'}
Volatility: High/Medium/Low (based on data)
        """
