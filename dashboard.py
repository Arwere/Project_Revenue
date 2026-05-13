import os
from datetime import datetime
from config import TOKEN_ADDRESS, TOKEN_SYMBOL, DASHBOARD_WIDTH, AGENT_NAME, RISK_LEVEL, TOKEN_NAME

def print_full_dashboard(token_metadata: dict, market_data: dict, stack_results: dict, decision: dict):
    os.system("cls" if os.name == "nt" else "clear")
    
    price_sol = market_data.get("price_sol", 0)
    usd_price = market_data.get("usd_price")
    volume = market_data.get("volume", 0)
    market_cap = market_data.get("market_cap")

    symbol = token_metadata.get("symbol", TOKEN_SYMBOL)
    name = token_metadata.get("name", TOKEN_NAME)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_score = decision.get("final_score", 0)

    print("=" * DASHBOARD_WIDTH)
    print(f"🚀 {AGENT_NAME} - JUPITER BOT | {now}")
    print("=" * DASHBOARD_WIDTH)
    print(f"Token : {name} ({symbol})")
    print(f"Mint  : {TOKEN_ADDRESS}")
    
    usd_str = f"${usd_price:.6f}" if usd_price and usd_price > 0 else "N/A"
    mcap_str = f"${market_cap:,.0f}" if market_cap and market_cap > 0 else "N/A"
    
    print(f"Price : {price_sol:.10f} SOL   |   {usd_str}")
    print(f"Market Cap : {mcap_str}      | 24h Vol : ${volume:,.0f}")
    print(f"Final Score: {final_score}/10")
    print("-" * DASHBOARD_WIDTH)

    print("🤖 MULTI-STACK RESULTS:")
    for name, res in decision.get("stack_results", {}).items():
        ind = res.get("indicators", {})
        print(f"   {name:15} → Score: {res.get('score', 0):.1f} | {res.get('recommendation', 'NEUTRAL')}")
    print("-" * DASHBOARD_WIDTH)

    # Risk Management
    risk_info = decision.get("risk", {})
    print("💰 RISK MANAGEMENT:")
    print(f"   Action        : {risk_info.get('action', 'HOLD')}")
    if risk_info.get("action") == "BUY":
        print(f"   Size          : {risk_info.get('size_sol', 0)} SOL")
        print(f"   Stop Loss     : {risk_info.get('stop_loss', 'N/A')}")
    print("-" * DASHBOARD_WIDTH)

    print("🤖 FINAL DECISION:")
    print(f"   Recommendation : {decision.get('recommendation', 'MONITOR')}")
    print(f"   Confidence     : {decision.get('confidence', 0)}/10")
    print(f"   Risk Level     : {RISK_LEVEL.upper()}")
    print("-" * DASHBOARD_WIDTH)

    print("REASONING:")
    for line in decision.get("reasoning", ["Waiting for data..."]):
        print(f"   • {line}")
    print("=" * DASHBOARD_WIDTH)
