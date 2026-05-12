import asyncio
import time
from collections import deque
from typing import Dict
from config import config
from data_fetcher import get_full_market_data, get_historical_prices
from dashboard import print_full_dashboard
from agent import TradingAgent
from jupiter_client import JupiterClient
from telegram_notifier import TelegramNotifier
from wallet import wallet_manager

class TradingSystem:
    def __init__(self):
        self.agent = TradingAgent()
        self.jupiter = JupiterClient()
        self.notifier = TelegramNotifier()
        self.price_histories: Dict[str, deque] = {}
        self.last_status = time.time()

        print(f"🚀 {config.AGENT_NAME} Multi-Token System Started!")
        print(f"Mode: {'🟢 LIVE' if not config.DRY_RUN else '🔒 DRY-RUN'}")
        print(f"Monitoring {len(config.TOKENS)} tokens\n")

    def get_history(self, symbol: str):
        if symbol not in self.price_histories:
            self.price_histories[symbol] = deque(maxlen=config.MAX_HISTORY_POINTS)
        return self.price_histories[symbol]

    async def process_token(self, token_key: str):
        token_config = config.TOKENS[token_key]
        symbol = token_config.symbol

        try:
            market_data = await get_full_market_data(token_config.address)
            history = self.get_history(symbol)
            
            prices_list = await get_historical_prices(token_config.address, limit=600)
            for p in prices_list:
                if p > 0:
                    history.append(p)

            decision = self.agent.get_risk_adjusted_decision(
                token_config=token_config,
                market_data=market_data,
                prices=list(history)
            )

            print_full_dashboard(token_config, market_data, decision)

            # Dry-run only for now
            if decision.get("action") == "BUY" and decision.get("final_score", 0) >= 7.5:
                print(f"   → Strong Buy Signal on {symbol} (Dry Run)")

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    async def run(self):
        if not wallet_manager.load():
            print("⚠️ Wallet not loaded - some features disabled")

        while True:
            try:
                tasks = [self.process_token(key) for key in config.TOKENS.keys()]
                await asyncio.gather(*tasks)
            except KeyboardInterrupt:
                print("\n\n🛑 Bot stopped by user.")
                break
            except Exception as e:
                print(f"Critical error: {e}")

            await asyncio.sleep(config.POLL_SECONDS)


if __name__ == "__main__":
    system = TradingSystem()
    asyncio.run(system.run())
