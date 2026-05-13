from typing import Dict

from config import config


class RiskManager:
    def get_trade_recommendation(self, decision: Dict, current_price: float, token_config=None):
        final_score = decision.get("final_score", 0)
        action = decision.get("action", "HOLD")

        if final_score >= 6.5 and action in ["BUY", "STRONG_BUY"]:
            return {
                "action": "BUY",
                "size_sol": 0.15,
                "stop_loss": round(current_price * 0.88, 10),
                "reason": f"Score {final_score:.1f}"
            }
        else:
            return {
                "action": "HOLD",
                "reason": "Below risk threshold"
            }


# Global instance
risk_manager = RiskManager()
