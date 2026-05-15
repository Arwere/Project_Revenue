import asyncio
import time
from liquidity_kraken import LiquidityKraken
from depth_destroyer import DepthDestroyer
from tide_titan import TideTitan
from config import config
from telegram_notifier import notifier

async def main():
    DRY_RUN = True
    enabled_tokens = config.get_enabled_tokens()

    print("🚀 Starting Master Controller - Dynamic Trading Bots")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'} | Enabled Tokens: {len(enabled_tokens)}")
    print("="*100)

    bots = {}
    bot_mapping = {
        "MM": TideTitan,
        "WHITEWHALE": DepthDestroyer,
        "TROLL": LiquidityKraken,
    }

    for token_key, token_cfg in enabled_tokens.items():
        BotClass = bot_mapping.get(token_key, TideTitan)
        bots[token_key] = BotClass(token_key, dry_run=DRY_RUN)
        print(f"✅ Deployed {BotClass.__name__} → {token_cfg.symbol}")

    if not bots:
        print("❌ No tokens enabled!")
        return

    print(f"\nAll {len(bots)} bots deployed. Live monitoring started.\n")
    print("="*100)

    cycle = 0
    while True:
        cycle += 1
        tasks = [bot.tick() for bot in bots.values()]
        await asyncio.gather(*tasks, return_exceptions=True)

        if cycle % 5 == 0:
            print(f"\n📊 LIVE STATUS - {time.strftime('%H:%M:%S')} (Cycle {cycle}) | Active: {len(bots)}")
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
        print("\n\n👋 Master stopped.")
    except Exception as e:
        print(f"Error: {e}")
