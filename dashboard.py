import os
from datetime import datetime
from typing import Dict, Any
from config import config

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_full_dashboard(token_config: Any, market_data: Dict, decision: Dict):
    clear_screen()
    
    symbol = token_config.symbol
    name = token_config.name
    address = token_config.address

    price_sol = market_data.get("price_sol", 0)
    usd_price = market_data.get("usd_price")
    volume = market_data.get("volume", 0)
    mcap = market_data.get("market_cap")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_score = decision.get("final_score", 0)

    print("=" * config.DASHBOARD_WIDTH)
    print(f"🚀 {config.AGENT_NAME} - MULTI TOKEN MONITOR | {now}")
    print("=" * config.DASHBOARD_WIDTH)
    print(f"Token : {name} ({symbol})")
    print(f"Mint  : {address}")
    print(f"Price : {price_sol:.10f} SOL   |   ${usd_price:.6f}" if usd_price else f"Price : {price_sol:.10f} SOL")
    if mcap:
        print(f"Market Cap : ${mcap:,.0f}    | 24h Vol : ${volume:,.0f}")
    print(f"Final Score: {final_score}/10")
    print("-" * config.DASHBOARD_WIDTH)

    print("🤖 STRATEGY STACK:")
    for name, res in decision.get("stack_results", {}).items():
        score = res.get("score", 0)
        print(f"   {name:15} → Score: {score:.1f} | {res.get('recommendation', 'NEUTRAL')}")

    print("-" * config.DASHBOARD_WIDTH)
    print("💰 RISK MANAGEMENT:")
    risk = decision.get("risk", {})
    print(f"   Action : {risk.get('action', 'HOLD')}")
    if risk.get("action") == "BUY":
        print(f"   Size   : {risk.get('size_sol', 0):.4f} SOL")
        print(f"   Stop Loss : {risk.get('stop_loss')}")

    print("-" * config.DASHBOARD_WIDTH)
    print("🤖 FINAL DECISION:")
    print(f"   Recommendation : {decision.get('recommendation', 'MONITOR')}")
    print(f"   Confidence     : {decision.get('confidence', 0)}/10")

    print("\nREASONING:")
    for line in decision.get("reasoning", ["Waiting for more data..."]):
        print(f"   • {line}")
    print("=" * config.DASHBOARD_WIDTH)
