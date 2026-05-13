import asyncio
import time
from liquidity_kraken import LiquidityKraken
from depth_destroyer import DepthDestroyer
from tide_titan import TideTitan
from config import config

# Global status storage
bot_status = {}

async def main():
    print("🚀 Starting Master Controller - 3 Specialized Trading Bots")
    print("="*100)

    bots = {}
    for token_key in config.TOKENS.keys():
        symbol = config.TOKENS[token_key].symbol
        if "TROLL" in symbol.upper():
            bots[token_key] = LiquidityKraken(token_key)
            bot_status[token_key] = {"name": "LIQUIDITY KRAKEN", "symbol": symbol}
        elif "WHALE" in symbol.upper():
            bots[token_key] = DepthDestroyer(token_key)
            bot_status[token_key] = {"name": "DEPTH DESTROYER", "symbol": symbol}
        else:
            bots[token_key] = TideTitan(token_key)
            bot_status[token_key] = {"name": "TIDE TITAN", "symbol": symbol}

        print(f"✅ Deployed {bot_status[token_key]['name']} → {symbol}")

    print("\nAll bots deployed. Live monitoring started.\n")
    print("="*100)

    cycle = 0
    while True:
        cycle += 1
        
        # Run all bots
        tasks = [bot.tick() for bot in bots.values()]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Clean status display every 5 cycles
        if cycle % 5 == 0:
            print(f"\n📊 LIVE STATUS - {time.strftime('%H:%M:%S')} (Cycle {cycle})")
            print("-" * 100)
            for key, status in bot_status.items():
                symbol = status["symbol"]
                print(f"{status['name']:<18} | {symbol:<12} | Status: Monitoring")
            print("-" * 100)

        await asyncio.sleep(8)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Master Controller stopped.")
    except Exception as e:
        print(f"\n💥 Error: {e}")
