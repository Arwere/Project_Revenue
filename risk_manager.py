from typing import Dict

class RiskManager:
    def get_conservative_position_size(self, score: float, current_price: float, token_config) -> float:
        """Conservative position sizing"""
        base = 0.25  # Max 25% of available capital per trade

        if score >= 8.0:
            return base * 0.95
        elif score >= 7.2:
            return base * 0.75
        elif score >= 6.8:
            return base * 0.55
        else:
            return 0.0  # No position if score too low

    def get_trade_recommendation(self, decision: Dict, price: float, token_config) -> Dict:
        """Basic risk check"""
        if decision.get("suggested_capital_percent", 0) <= 0:
            return {"action": "BLOCK"}
        return {"action": "APPROVED"}
