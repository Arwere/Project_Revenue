import asyncio
import time
import os
from data_fetcher import get_price_in_sol, get_historical_prices
from agent import Poseidon
from config import config

token_states = {}

async def monitor_token(token_key: str):
    token_config = config.TOKENS[token_key]
    agent = Poseidon()
    
    print(f"📡 Monitor started → {token_config.symbol}")
    
    while True:
        try:
            current_price = await get_price_in_sol(token_config.address)
            if current_price <= 0:
                await asyncio.sleep(5)
                continue

            prices = await get_historical_prices(token_config.address, limit=400)

            decision = agent.get_risk_adjusted_decision(
                token_config, 
                {"price_sol": current_price}, 
                prices, 
                bot_name="Dashboard"
            )

            token_states[token_key] = {
                "symbol": token_config.symbol,
                "price": current_price,
                "score": decision.get("final_score", 0),
                "action": decision.get("action", "HOLD"),
                "last_update": time.time()
            }

        except Exception:
            pass
        await asyncio.sleep(7)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_moon_tide_dashboard():
    clear_screen()
    print("="*150)
    print(f"🌊 MOON TIDE DASHBOARD - {time.strftime('%Y-%m-%d %H:%M:%S')} | DRY RUN MODE")
    print("="*150)
    print(f"🤖 AGENT: POSEIDON (Multi-Timeframe Analysis)")
    print("-"*150)
    print(f"{'BOT NAME':<20} {'SYMBOL':<12} {'PRICE (SOL)':<15} {'SCORE':<8} {'ACTION':<12} {'STATUS'}")
    print("-"*150)

    for key, state in token_states.items():
        symbol = state.get("symbol", key)
        price = state.get("price", 0)
        score = state.get("score", 0)
        action = state.get("action", "HOLD")
        
        color = "🟢" if action in ["BUY", "STRONG_BUY"] else "🔴" if action == "SELL" else "⚪"
        bot_name = "LIQUIDITY KRAKEN" if "TROLL" in symbol.upper() else "DEPTH DESTROYER" if "WHALE" in symbol.upper() else "TIDE TITAN"
        
        print(f"{color} {bot_name:<18} {symbol:<12} {price:.8f}      {score:.1f}     {action:<12} Monitoring")

    print("-"*150)
    print("📌 Poseidon is actively monitoring all 3 tokens | Dry Run Mode | Ctrl+C to stop")
    print("="*150)


async def main():
    print("Starting Moon Tide Dashboard...\n")
    
    for key in config.TOKENS.keys():
        asyncio.create_task(monitor_token(key))
    
    while True:
        print_moon_tide_dashboard()
        await asyncio.sleep(8)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nMoon Tide Dashboard stopped by user.")
    except Exception as e:
        print(f"Dashboard error: {e}")
