import time
from collections import deque
from datetime import datetime

from config import TOKEN_ADDRESS, POLL_SECONDS, AGENT_NAME, DRY_RUN
from agent import TradingAgent
from utils import get_token_metadata, get_price_in_sol, get_usd_price, get_24h_volume, get_market_cap
from dashboard import print_full_dashboard
from jupiter_client import JupiterClient
from telegram_notifier import TelegramNotifier

def main():
    agent = TradingAgent()
    jupiter = JupiterClient()
    notifier = TelegramNotifier()
    history = deque(maxlen=10000)

    print(f"🚀 {AGENT_NAME} Jupiter Bot Started!")
    print(f"Mode: {'🟢 LIVE' if not DRY_RUN else '🔒 DRY-RUN MODE'}")
    print(f"Telegram: Enabled (Topic 19)\n")

    last_status_time = time.time()

    while True:
        try:
            token_metadata = get_token_metadata()
            price_sol = get_price_in_sol()

            history.append({"price_sol": price_sol})
            prices = [s["price_sol"] for s in history if s["price_sol"] > 0]

            market_data = {
                "price_sol": price_sol,
                "usd_price": get_usd_price(),
                "volume": get_24h_volume(token_metadata),
                "market_cap": get_market_cap(token_metadata)
            }

            decision = agent.get_risk_adjusted_decision(market_data, prices)

            print_full_dashboard(token_metadata, market_data, decision.get("stack_results", {}), decision)

            # === TELEGRAM ALERTS ===
            current_score = decision.get("final_score", 0)

            if decision.get("action") == "BUY":
                size_sol = decision.get("risk", {}).get("size_sol", 0)
                notifier.send_strong_buy(
                    token_symbol=token_metadata.get("symbol", "MM"),
                    price=price_sol,
                    size_sol=size_sol,
                    score=current_score
                )

            # Status Update every 30 minutes
            if time.time() - last_status_time > 1800:   # 30 minutes
                action = decision.get("action", "HOLD")
                notifier.send_status_update(
                    token_symbol=token_metadata.get("symbol", "MM"),
                    score=current_score,
                    price=price_sol,
                    action=action
                )
                last_status_time = time.time()

        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user.")
            notifier.send_message("🛑 Bot has been stopped by user.")
            break
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()
