cat > tide_titan.py << 'EOF'
import asyncio
import time
from agent import TradingAgent
from data_fetcher import get_price_in_sol, get_historical_prices
from config import config

class TideTitan:
    """Balanced steady trader bot"""
    
    def __init__(self, token_key: str, dry_run=True):
        self.token_key = token_key
        self.config = config.TOKENS[token_key]
        self.agent = TradingAgent()
        self.dry_run = dry_run
        self.position = 0.0
        self.entry_price = 0.0
        self.cooldown_until = 0

    async def tick(self):
        try:
            current_price = await get_price_in_sol(self.config.address)
            if current_price <= 0:
                return

            prices = await get_historical_prices(self.config.address, limit=500)
            decision = self.agent.get_risk_adjusted_decision(
                self.config, {"price_sol": current_price}, prices, bot_name="TideTitan"
            )

            action = decision.get("action", "HOLD")
            score = decision.get("final_score", 0)

            if action != "HOLD" or score >= 7.0:
                print(f"[TIDE TITAN - {self.config.symbol}] Price: {current_price:.8f} | Score: {score:.1f} | Action: {action}")

            if time.time() < self.cooldown_until:
                return

            if action in ["BUY", "STRONG_BUY"] and self.position == 0:
                if self.dry_run:
                    print(f"[DRY RUN] TIDE TITAN would BUY {self.config.symbol}")
                else:
                    print(f"[LIVE] TIDE TITAN executing BUY on {self.config.symbol}")
            elif action == "SELL" and self.position > 0:
                if self.dry_run:
                    print(f"[DRY RUN] TIDE TITAN would SELL {self.config.symbol}")
                else:
                    print(f"[LIVE] TIDE TITAN executing SELL on {self.config.symbol}")

        except Exception as e:
            print(f"[TIDE TITAN] Error: {e}")
EOF
