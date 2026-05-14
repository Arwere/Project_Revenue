cat > master.py << 'EOF'
import asyncio
import time
from liquidity_kraken import LiquidityKraken
from depth_destroyer import DepthDestroyer
from tide_titan import TideTitan
from config import config

async def main():
    DRY_RUN = True   # ← Change to False when ready for real trades

    print("🚀 Starting Master Controller - 3 Specialized Trading Bots")
    print(f"Mode: {'DRY RUN (Safe)' if DRY_RUN else 'LIVE TRADING'}")
    print("="*100)

    bots = {}
    for token_key in config.TOKENS.keys():
        symbol = config.TOKENS[token_key].symbol
        if "TROLL" in symbol.upper():
            bots[token_key] = LiquidityKraken(token_key, dry_run=DRY_RUN)
            print(f"✅ Deployed LIQUIDITY KRAKEN → {symbol}")
        elif "WHALE" in symbol.upper():
            bots[token_key] = DepthDestroyer(token_key, dry_run=DRY_RUN)
            print(f"✅ Deployed DEPTH DESTROYER → {symbol}")
        else:
            bots[token_key] = TideTitan(token_key, dry_run=DRY_RUN)
            print(f"✅ Deployed TIDE TITAN → {symbol}")

    print("\nAll bots deployed. Live monitoring started.\n")
    print("="*100)

    cycle = 0
    while True:
        cycle += 1
        tasks = [bot.tick() for bot in bots.values()]
        await asyncio.gather(*tasks, return_exceptions=True)

        if cycle % 5 == 0:
            print(f"\n📊 LIVE STATUS - {time.strftime('%H:%M:%S')} (Cycle {cycle})")
            print("-" * 100)
            for key, bot in bots.items():
                symbol = config.TOKENS[key].symbol
                print(f"{bot.__class__.__name__:<20} | {symbol:<12} | Monitoring")
            print("-" * 100)

        await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Master stopped by user.")
EOF
