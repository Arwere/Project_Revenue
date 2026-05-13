import os
from datetime import datetime
from typing import Dict, Any

from config import config


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def simple_sparkline(prices, length=8):
    """Simple ASCII sparkline"""
    if len(prices) < 2:
        return "──────"
    recent = prices[-length:]
    min_p, max_p = min(recent), max(recent)
    if max_p == min_p:
        return "──────"
    
    spark = "▁▂▃▄▅▆▇█"
    line = ""
    for p in recent:
        idx = int((p - min_p) / (max_p - min_p + 0.000001) * 7)
        line += spark[idx]
    return line


def print_multi_token_dashboard(all_data: list):
    clear_screen()
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("=" * config.DASHBOARD_WIDTH)
    print(f"🚀 {config.AGENT_NAME} — PROFESSIONAL MULTI-TOKEN DASHBOARD | {now}")
    print("=" * config.DASHBOARD_WIDTH)
    print(f"Monitoring {len(config.TOKENS)} tokens | Mode: {'🟢 LIVE' if not config.DRY_RUN else '🔒 DRY-RUN'} | Data: Birdeye + Jupiter")
    print("-" * config.DASHBOARD_WIDTH)

    for item in all_data:
        tc = item["token_config"]
        md = item["market_data"]
        dec = item["decision"]
        
        symbol = tc.symbol
        name = tc.name
        price_sol = md.get("price_sol", 0)
        usd = md.get("usd_price")
        score = dec.get("final_score", 0)
        action = dec.get("action", "HOLD")
        rec = dec.get("recommendation", "MONITOR")

        # Color coding
        color = "🟢" if score >= 7.5 else "🟡" if score >= 5 else "🔴"
        action_color = "🟢" if action in ["BUY", "STRONG_BUY"] else "🔴"

        usd_str = f"${usd:.6f}" if usd and usd > 0 else "N/A"

        print(f"{color} {name:<14} ({symbol})")
        print(f"   Price : {price_sol:.10f} SOL   |   {usd_str}")

        # Sparkline + Trend
        history = item.get("history", [])
        if len(history) > 8:
            spark = simple_sparkline(history)
            print(f"   Trend : {spark}  (Recent movement)")

        print(f"   Score : {score:.1f}/10    | Action: {action_color} {action:<8} | Rec: {rec}")

        # Agent Stack
        stack = dec.get("stack_results", {})
        if stack:
            parts = [f"{name[:5]}:{res.get('score',0):.1f}" for name, res in stack.items()]
            print(f"   Agent : {' | '.join(parts)}")

        # Reasoning
        reasoning = dec.get("reasoning", [])
        if reasoning:
            print(f"   Insight: {reasoning[0][:95]}{'...' if len(reasoning[0]) > 95 else ''}")

        print("-" * 95)

    print("=" * config.DASHBOARD_WIDTH)
    print("💡 Ctrl+C to stop • Live updates every ~12s • Press any key for manual refresh (coming soon)")
    print("=" * config.DASHBOARD_WIDTH)
