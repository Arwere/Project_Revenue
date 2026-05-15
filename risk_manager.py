from typing import Dict

class RiskManager:
    def get_conservative_position_size(self, score: float, current_price: float, token_config) -> float:
        """Very conservative position sizing"""
        if score < 6.5:
            return 0.0
        elif score >= 8.2:
            return 0.22   # Max 22% of capital
        elif score >= 7.5:
            return 0.18
        elif score >= 6.8:
            return 0.12
        else:
            return 0.06

    def get_trade_recommendation(self, decision: Dict, price: float, token_config) -> Dict:
        if decision.get("suggested_capital_percent", 0) <= 0.01:
            return {"action": "BLOCK"}
        return {"action": "APPROVED"}
