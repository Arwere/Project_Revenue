from typing import Dict, List
from config import config
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Position:
    symbol: str
    entry_price: float
    size_sol: float
    stop_loss: float
    take_profit_levels: List[float]
    timestamp: str

class RiskManager:
    def __init__(self):
        self.portfolio_value_sol = 0.0
        self.positions: Dict[str, Position] = {}
        self.total_exposure_sol = 0.0

    def update_portfolio_value(self, total_sol: float):
        self.portfolio_value_sol = total_sol

    def calculate_position_size(self, confidence: int, token_config=None) -> float:
        if self.portfolio_value_sol <= 0:
            return config.MIN_TRADE_AMOUNT_SOL

        max_pos = getattr(token_config, 'max_position_size', config.MAX_POSITION_SIZE)
        base_size = self.portfolio_value_sol * config.DEFAULT_POSITION_SIZE
        multiplier = min(1.0, confidence / 8.5)

        size = base_size * multiplier
        size = min(size, self.portfolio_value_sol * max_pos)
        size = min(size, config.MAX_TRADE_AMOUNT_SOL)
        size = max(size, config.MIN_TRADE_AMOUNT_SOL)

        # Global exposure limit
        remaining = self.portfolio_value_sol * 0.65 - self.total_exposure_sol
        size = min(size, max(0.0, remaining))

        return round(size, 4)

    def get_trade_recommendation(self, decision: Dict, current_price: float, token_config=None):
        rec = decision.get("recommendation", "MONITOR")
        confidence = decision.get("confidence", 5)
        final_score = decision.get("final_score", 0)
        symbol = decision.get("token") or getattr(token_config, 'symbol', 'UNKNOWN')

        if rec in ["STRONG_BUY", "BUY"] and final_score >= 6.5 and confidence >= 6:
            size_sol = self.calculate_position_size(confidence, token_config)
            
            return {
                "action": "BUY",
                "size_sol": size_sol,
                "stop_loss": round(current_price * (1 + config.STOP_LOSS_PCT), 10),
                "take_profit_levels": [round(current_price * (1 + tp), 10) for tp in config.TAKE_PROFIT_LEVELS],
                "reason": f"Strong signal (Score {final_score:.1f})"
            }

        return {"action": "HOLD", "reason": "No strong signal"}
