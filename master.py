import asyncio
import time
from datetime import datetime
import os

# Import core components
from config import config
from position_manager import PositionManager
from jupiter_client import JupiterClient

# Import specialized bots
from tide_titan import TideTitan
from depth_destroyer import DepthDestroyer
from liquidity_kraken import LiquidityKraken

class MoonTideMaster:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.position_manager = PositionManager()
        self.jupiter = JupiterClient()
        
        self.bots = {}
        self.running = False
        
        # Initialize enabled bots
        self._initialize_bots()

    def _initialize_bots(self):
        """Create one bot per enabled token"""
        for token_key, token_config in config.TOKENS.items():
            # token_config is a TokenConfig dataclass, not a dict
            if not token_config.enabled:
                print(f"⏭️  Skipping disabled token: {token_config.symbol}")
                continue

            print(f"🚀 Initializing bot for {token_config.symbol} ({token_key})")

            if token_key.lower() == "mm" or token_key == "MM":
                self.bots[token_key] = TideTitan(
                    token_key, self.position_manager, self.jupiter, self.dry_run
                )
            elif token_key.lower() == "whitewhale":
                self.bots[token_key] = DepthDestroyer(
                    token_key, self.position_manager, self.jupiter, self.dry_run
                )
            elif token_key.lower() == "troll":
                self.bots[token_key] = LiquidityKraken(
                    token_key, self.position_manager, self.jupiter, self.dry_run
                )
            else:
                # Default fallback
                self.bots[token_key] = TideTitan(
                    token_key, self.position_manager, self.jupiter, self.dry_run
                )

    async def tick_all(self):
        """Run one cycle for all bots"""
        tasks = [bot.tick() for bot in self.bots.values()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def run(self):
        """Main trading loop"""
        self.running = True
        print(f"🌊 Moon Tide Master started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {'🟢 LIVE' if not self.dry_run else '🔒 DRY-RUN'}")
        print(f"Active bots: {list(self.bots.keys())}")
        print("-" * 70)

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
            sleep_time = max(10.0 - elapsed, 5.0)

            await asyncio.sleep(sleep_time)

    def _print_portfolio_status(self):
        """Print summary of all positions"""
        positions = self.position_manager.get_all_positions()
        if not positions:
            print("📊 No open positions")
            return

        print(f"\n📊 PORTFOLIO STATUS ({len(positions)} open positions)")
        total_invested = self.position_manager.total_sol_invested
        print(f"Total Invested : {total_invested:.4f} SOL")

        for token_key, pos in positions.items():
            if pos.status == "OPEN":
                pnl = ((pos.amount * pos.entry_price) - pos.sol_invested) / pos.sol_invested * 100 if pos.sol_invested > 0 else 0
                print(f"   • {pos.symbol:12} | {pos.amount:.4f} tokens @ {pos.entry_price:.8f} SOL | PnL: {pnl:+.2f}%")
        print("-" * 70)

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
