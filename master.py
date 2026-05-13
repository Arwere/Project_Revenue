import asyncio
import time
from collections import deque
from typing import Dict

from config import config
from data_fetcher import get_full_market_data, get_historical_prices
from dashboard import print_multi_token_dashboard
from agent import TradingAgent
from wallet import wallet_manager


class TradingSystem:
    def __init__(self):
        self.agent = TradingAgent()
        self.price_histories: Dict[str, deque] = {}
        self.running = True

        print(f"🚀 {config.AGENT_NAME} — Glam Dashboard Mode Activated!")
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
            
            prices = await get_historical_prices(token_config.address, limit=120)
            for p in prices:
                if p > 0:
                    history.append(p)

            decision = self.agent.get_risk_adjusted_decision(
                token_config=token_config,
                market_data=market_data,
                prices=list(history)
            )

            return {
                "token_config": token_config,
                "market_data": market_data,
                "decision": decision,
                "history": list(history)[-30:]   # Last 30 prices for sparkline
            }

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            return None

    async def run(self):
        wallet_manager.load()
        print("✅ Glam Dashboard Running...\n")

        try:
            while self.running:
                tasks = [self.process_token(key) for key in config.TOKENS.keys()]
                results = await asyncio.gather(*tasks)

                valid_results = [r for r in results if r is not None]
                if valid_results:
                    print_multi_token_dashboard(valid_results)

                await asyncio.sleep(config.POLL_SECONDS)

        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\n\n🛑 Stopped gracefully.")
        finally:
            print("👋 Multi_Token_Agent stopped.")


if __name__ == "__main__":
    system = TradingSystem()
    asyncio.run(system.run())
