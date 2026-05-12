import requests
import time
from config import config

class TelegramNotifier:
    def __init__(self):
        self.enabled = config.TELEGRAM_ENABLED and config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.thread_id = 19
        self.base_url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        self.last_alert = 0
        self.cooldown = 300  # 5 minutes

    def send_message(self, text: str, silent: bool = False):
        if not self.enabled:
            return False
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            if self.thread_id:
                payload["message_thread_id"] = self.thread_id
            if silent:
                payload["disable_notification"] = True

            r = requests.post(self.base_url, json=payload, timeout=10)
            return r.status_code == 200
        except:
            return False

    def send_strong_buy(self, token_symbol: str, price: float, size_sol: float, score: float):
        if time.time() - self.last_alert < self.cooldown:
            return False

        mode = "LIVE" if not config.DRY_RUN else "DRY-RUN"
        msg = f"""
🚨 <b>STRONG BUY SIGNAL</b> 🚨

Token: <b>{token_symbol}</b>
Price: <b>{price:.10f} SOL</b>
Size: <b>{size_sol:.4f} SOL</b>
Score: <b>{score}/10</b>
Mode: {mode}
Time: {time.strftime("%H:%M:%S")}
        """.strip()

        success = self.send_message(msg)
        if success:
            self.last_alert = time.time()
            print(f"✅ Telegram alert sent for {token_symbol}")
        return success
