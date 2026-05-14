import asyncio
import time
from data_fetcher import get_price_in_sol, get_historical_prices
from agent import Poseidon
from config import config

token_states = {}

async def monitor_token(token_key: str):
    token_config = config.TOKENS[token_key]
    agent = Poseidon()
    
    print(f"📡 Monitor started for {token_config.symbol}")
    
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

        except Exception as e:
            print(f"Monitor error for {token_config.symbol}: {e}")

        await asyncio.sleep(6)  # Balanced update rate


def print_dashboard():
    print("\n" + "="*120)
    print(f"🌊 POSEIDON LIVE DASHBOARD - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*120)

    if not token_states:
        print("Waiting for first data from monitors...")
    else:
        for key, state in token_states.items():
            symbol = state.get("symbol", key)
            price = state.get("price", 0)
            score = state.get("score", 0)
            action = state.get("action", "HOLD")
            
            color = "🟢" if action in ["BUY", "STRONG_BUY"] else "🔴" if action == "SELL" else "⚪"
            print(f"{color} {symbol:<12} | Price: {price:.8f} SOL | Score: {score:.1f} | Action: {action:<12}")

    print("="*120)


async def main():
    print("Starting Poseidon Live Dashboard...\n")
    
    # Start monitors
    monitor_tasks = [monitor_token(key) for key in config.TOKENS.keys()]
    
    # Dashboard display loop
    while True:
        print_dashboard()
        await asyncio.sleep(8)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDashboard stopped by user.")
    except Exception as e:
        print(f"Dashboard crashed: {e}")
