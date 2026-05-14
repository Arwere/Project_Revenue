cat > tide_titan.py << 'EOF'
import asyncio
import time
from agent import TradingAgent
from data_fetcher import get_price_in_sol, get_historical_prices
from jupiter_client import JupiterClient
from wallet import load_wallet
from config import config

class TideTitan:
    """Balanced steady trader bot"""
    
    def __init__(self, token_key: str):
        self.token_key = token_key
        self.config = config.TOKENS[token_key]
        self.agent = TradingAgent()
        self.jupiter = JupiterClient()
        self.wallet = load_wallet()
        
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
                await self._execute_buy(current_price, decision)
            elif action == "SELL" and self.position > 0:
                await self._execute_sell(current_price, decision)

        except Exception as e:
            print(f"[TIDE TITAN] Error: {e}")

    async def _execute_buy(self, price: float, decision: dict):
        amount_sol = self.wallet.get_available_sol() * decision.get("suggested_capital_percent", 0.25)
        if amount_sol < 0.05:
            return
        print(f"[TIDE TITAN] Executing BUY {amount_sol:.4f} SOL → {self.config.symbol}")
        tx = await self.jupiter.swap_sol_to_token(self.config.address, amount_sol, slippage=1.2)
        if tx:
            self.position = (amount_sol / price) * 0.98
            self.entry_price = price
            print(f"[TIDE TITAN] BUY SUCCESS")

    async def _execute_sell(self, price: float, decision: dict):
        if self.position <= 0:
            return
        print(f"[TIDE TITAN] Executing SELL")
        tx = await self.jupiter.swap_token_to_sol(self.config.address, self.position, slippage=1.2)
        if tx:
            self.position = 0.0
            self.cooldown_until = time.time() + 300
            print(f"[TIDE TITAN] SELL SUCCESS")

if __name__ == "__main__":
    print("Tide Titan initialized")
EOF
