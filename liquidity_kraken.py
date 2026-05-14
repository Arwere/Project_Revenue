import asyncio
import time
from agent import Poseidon
from data_fetcher import get_price_in_sol, get_historical_prices
from telegram_notifier import notifier
from config import config

class LiquidityKraken:
    def __init__(self, token_key: str, dry_run=True):
        self.token_key = token_key
        self.config = config.TOKENS[token_key]
        self.agent = Poseidon()          # ← Updated
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
                self.config, {"price_sol": current_price}, prices, bot_name="LiquidityKraken"
            )

            action = decision.get("action", "HOLD")
            score = decision.get("final_score", 0)

            if action != "HOLD" or score >= 7.0:
                print(f"[LIQUIDITY KRAKEN - {self.config.symbol}] Price: {current_price:.8f} | Score: {score:.1f} | Action: {action}")

            if time.time() < self.cooldown_until:
                return

            if action in ["BUY", "STRONG_BUY"] and self.position == 0:
                capital = decision.get("suggested_capital_percent", 0.0) * 100
                msg = f"<b>🟢 LIQUIDITY KRAKEN</b>\n{self.config.symbol}: BUY Signal\nScore: {score:.1f}\nCapital: {capital:.1f}%\nPrice: {current_price:.8f}"
                await notifier.send_message(msg)
                print(f"[LIQUIDITY KRAKEN] → BUY SIGNAL on {self.config.symbol}")

            elif action == "SELL" and self.position > 0:
                msg = f"<b>🔴 LIQUIDITY KRAKEN</b>\n{self.config.symbol}: SELL Signal\nPrice: {current_price:.8f}"
                await notifier.send_message(msg)
                print(f"[LIQUIDITY KRAKEN] → SELL SIGNAL on {self.config.symbol}")

        except Exception as e:
            print(f"[LIQUIDITY KRAKEN] Error: {e}")
