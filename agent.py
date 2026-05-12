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
        self.memory: Dict[str, List[Dict]] = {}

    def analyze(self, token_config, market_data: Dict, prices: List[float]) -> Dict:
        symbol = token_config.symbol
        
        if len(prices) < config.MIN_DATA_POINTS:
            return {
                "recommendation": "MONITOR",
                "confidence": 4,
                "final_score": 0.0,
                "reasoning": [f"Collecting data... ({len(prices)}/{config.MIN_DATA_POINTS})"],
                "stack_results": {},
                "token": symbol
            }

        results = {}
        weighted_score = 0.0
        total_weight = 0.0
        reasoning = []

        weights = token_config.strategy_weights or config.STRATEGY_WEIGHTS

        for name, strategy in self.strategies.items():
            result = strategy.analyze(prices, market_data, token_config)
            results[name] = result
            weight = weights.get(name, 0.25)
            weighted_score += result["score"] * weight
            total_weight += weight
            reasoning.append(f"{name}: {result.get('reason', 'No signal')}")

        final_score = weighted_score / total_weight if total_weight > 0 else 5.0

        if final_score >= 8.0:
            rec, conf = "STRONG_BUY", 9
        elif final_score >= 6.5:
            rec, conf = "BUY", 7
        elif final_score <= 3.5:
            rec, conf = "REDUCE", 6
        else:
            rec, conf = "MONITOR", 5

        decision = {
            "recommendation": rec,
            "confidence": conf,
            "final_score": round(final_score, 2),
            "stack_results": results,
            "reasoning": reasoning,
            "token": symbol
        }

        # Memory
        if symbol not in self.memory:
            self.memory[symbol] = []
        self.memory[symbol].append(decision)
        if len(self.memory[symbol]) > 200:
            self.memory[symbol].pop(0)

        return decision

    def get_risk_adjusted_decision(self, token_config, market_data: Dict, prices: List[float]) -> Dict:
        base = self.analyze(token_config, market_data, prices)
        current_price = market_data.get("price_sol", 0)

        if current_price > 0:
            risk_info = self.risk_manager.get_trade_recommendation(base, current_price, token_config)
            base["risk"] = risk_info
            base["action"] = risk_info.get("action", "HOLD")
        else:
            base["action"] = "HOLD"

        return base
