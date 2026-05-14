import asyncio
import time
from liquidity_kraken import LiquidityKraken
from depth_destroyer import DepthDestroyer
from tide_titan import TideTitan
from config import config
from telegram_notifier import notifier

async def main():
    DRY_RUN = True

    print("🚀 Starting Master Controller - 3 Specialized Trading Bots")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print("="*100)

    bots = {}
    for token_key in config.TOKENS.keys():
        symbol = config.TOKENS[token_key].symbol
        if "TROLL" in symbol.upper():
            bots[token_key] = LiquidityKraken(token_key, dry_run=DRY_RUN)
        elif "WHALE" in symbol.upper():
            bots[token_key] = DepthDestroyer(token_key, dry_run=DRY_RUN)
        else:
            bots[token_key] = TideTitan(token_key, dry_run=DRY_RUN)

        print(f"✅ Deployed {bots[token_key].__class__.__name__} → {symbol}")

    print("\nAll bots deployed. Live monitoring started.\n")
    print("="*100)

    cycle = 0
    while True:
        cycle += 1
        tasks = [bot.tick() for bot in bots.values()]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Poseidon Status Update (every 30 seconds)
        if cycle % 3 == 0:
            status_msg = f"""<b>🌊 POSEIDON STATUS REPORT</b>
Time: {time.strftime('%H:%M:%S')}
Cycle: {cycle}
Mode: {'🟡 DRY RUN' if DRY_RUN else '🔴 LIVE'}
Active Bots: 3
Tokens Monitored: MM, WHITEWHALE, TROLL

📈 All bots are actively analyzing multi-timeframe data."""
            await notifier.send_message(status_msg, topic_id=13)

        if cycle % 6 == 0:
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
    except Exception as e:
        print(f"💥 Error: {e}")
