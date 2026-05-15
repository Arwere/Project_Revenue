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
    print(f"📡 Dashboard monitor started → {token_config.symbol}")
    
    while True:
        try:
            current_price = await get_price_in_sol(token_config.address)
            prices = await get_historical_prices(token_config.address, limit=400)

            decision = await agent.get_risk_adjusted_decision(
                token_config, {"price_sol": current_price}, prices, bot_name="Dashboard"
            )

            token_states[token_key] = {
                "symbol": token_config.symbol,
                "price": current_price,
                "score": decision.get("final_score", 0),
                "action": decision.get("action", "HOLD"),
                "last_update": time.time()
            }
        except:
            pass
        await asyncio.sleep(9)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_moon_tide_dashboard():
    clear_screen()
    print("="*140)
    print(f"🌊 MOON TIDE DASHBOARD - {time.strftime('%Y-%m-%d %H:%M:%S')} | DRY RUN MODE")
    print("="*140)
    print("🤖 AGENT: POSEIDON (Multi-Timeframe Analysis)")
    print("-"*140)
    print(f"{'BOT NAME':<20} {'SYMBOL':<12} {'PRICE (SOL)':<15} {'SCORE':<8} {'ACTION':<12} STATUS")
    print("-"*140)

    enabled = config.get_enabled_tokens()
    for key in enabled.keys():
        state = token_states.get(key, {})
        symbol = state.get("symbol", enabled[key].symbol)
        price = state.get("price", 0.0)
        score = state.get("score", 0.0)
        action = state.get("action", "HOLD")
        
        color = "🟢" if action in ["BUY", "STRONG_BUY"] else "🔴" if action == "SELL" else "⚪"
        bot_name = "LIQUIDITY KRAKEN" if key == "TROLL" else "DEPTH DESTROYER" if key == "WHITEWHALE" else "TIDE TITAN"
        
        print(f"{color} {bot_name:<18} {symbol:<12} {price:.8f}      {score:.1f}     {action:<12} Monitoring")

    print("-"*140)
    print(f"📌 Monitoring {len(enabled)} tokens | Dry Run Mode | Ctrl+C to stop")
    print("="*140)

async def main():
    print("Starting Moon Tide Dashboard...\n")
    
    for key in config.get_enabled_tokens().keys():
        asyncio.create_task(monitor_token(key))
    
    while True:
        print_moon_tide_dashboard()
        await asyncio.sleep(8)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
