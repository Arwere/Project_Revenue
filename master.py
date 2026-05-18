import asyncio
import time
from datetime import datetime

from config import config
from portfolio import Portfolio
from jupiter_client import JupiterClient
from wallet_manager import WalletManager

# Import bots
from tide_titan import TideTitan
from depth_destroyer import DepthDestroyer
from liquidity_kraken import LiquidityKraken

class MoonTideMaster:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.wallet = WalletManager()
        
        # Initial capital (will be refreshed async)
        self.total_capital_sol = 50.0
        self.portfolio = Portfolio(
            total_capital_sol=self.total_capital_sol, 
            wallet_manager=self.wallet
        )
        
        self.jupiter = JupiterClient()
        self.bots = {}
        self.running = False
        
        self._initialize_bots()

    def _initialize_bots(self):
        for token_key, token_config in config.TOKENS.items():
            if not token_config.enabled:
                print(f"⏭️  Skipping disabled token: {token_config.symbol}")
                continue

            print(f"🚀 Initializing bot for {token_config.symbol} ({token_key})")

            if token_key.lower() == "mm":
                bot_class = TideTitan
            elif token_key.lower() == "whitewhale":
                bot_class = DepthDestroyer
            elif token_key.lower() == "troll":
                bot_class = LiquidityKraken
            else:
                bot_class = TideTitan

            self.bots[token_key] = bot_class(
                token_key, self.portfolio, self.jupiter, self.dry_run
            )

    async def initialize_portfolio(self):
        """Async initialization - refresh real wallet balance"""
        print("💰 Refreshing portfolio capital from wallet...")
        await self.portfolio.refresh_capital()
        self.total_capital_sol = self.portfolio.total_capital_sol

    async def tick_all(self):
        tasks = [bot.tick() for bot in self.bots.values()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def run(self):
        self.running = True
        
        # Initialize wallet balance before starting main loop
        await self.initialize_portfolio()

        print(f"🌊 Moon Tide Master started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {'🟢 LIVE' if not self.dry_run else '🔒 DRY-RUN'}")
        print(f"Total Trading Capital: {self.total_capital_sol:.4f} SOL")
        print(f"Active tokens: {list(self.bots.keys())}")
        print("-" * 85)

        cycle = 0
        while self.running:
            cycle += 1
            start_time = time.time()

            try:
                await self.tick_all()

                # Portfolio status every 5 cycles
                if cycle % 5 == 0:
                    self._print_portfolio_status()

            except Exception as e:
                print(f"❌ Master cycle error: {e}")

            elapsed = time.time() - start_time
            await asyncio.sleep(max(10.0 - elapsed, 5.0))

    def _print_portfolio_status(self):
        summary = self.portfolio.get_summary()
        print(summary)

        positions = self.portfolio.get_all_positions()
        if positions:
            print("Open Positions:")
            for pos in positions.values():
                if pos.status == "OPEN":
                    print(f"   • {pos.symbol:12} | {pos.amount:.4f} tokens @ {pos.entry_price:.8f} SOL")
        else:
            print("   No open positions.")
        print("-" * 85)

    def stop(self):
        self.running = False
        print("🛑 Moon Tide Master shutting down...")


# ====================== ENTRY POINT ======================
if __name__ == "__main__":
    import sys

    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] in ["--live", "-l", "--real"]:
        dry_run = False
        print("⚠️  LIVE MODE ENABLED - Real trades will be executed!")

    master = MoonTideMaster(dry_run=dry_run)

    try:
        asyncio.run(master.run())
    except KeyboardInterrupt:
        master.stop()
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        master.stop()
