import requests
import time
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ENABLED

class TelegramNotifier:
    def __init__(self):
        self.enabled = TELEGRAM_ENABLED and TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE"
        self.chat_id = TELEGRAM_CHAT_ID
        self.message_thread_id = 19
        self.base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        self.last_alert_time = 0
        self.alert_cooldown = 300   # 5 minutes for important alerts

    def send_message(self, message: str, silent: bool = False):
        if not self.enabled:
            return False
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            if self.message_thread_id:
                payload["message_thread_id"] = self.message_thread_id
            if silent:
                payload["disable_notification"] = True

            response = requests.post(self.base_url, json=payload, timeout=10)
            return response.status_code == 200
        except:
            return False

    def send_strong_buy(self, token_symbol: str, price: float, size_sol: float, score: float):
        """Only send when bot is about to enter a position"""
        if time.time() - self.last_alert_time < self.alert_cooldown:
            return False

        message = f"""
🚨 <b>STRONG BUY SIGNAL - ENTERING POSITION</b> 🚨

Token: <b>{token_symbol}</b>
Price: <b>{price:.10f} SOL</b>
Size: <b>{size_sol:.3f} SOL</b>
Confluence Score: <b>{score}/10</b>
Time: {time.strftime("%H:%M:%S")}
Mode: DRY-RUN
        """.strip()
        
        self.send_message(message)
        self.last_alert_time = time.time()
        print("✅ Strong Buy Alert sent to Telegram")
        return True

    def send_status_update(self, token_symbol: str, score: float, price: float, action: str):
        """Periodic status update"""
        message = f"""
🤖 <b>Status Update</b>

Token: <b>{token_symbol}</b>
Price: {price:.10f} SOL
Current Score: <b>{score}/10</b>
Action: <b>{action}</b>
Time: {time.strftime("%H:%M:%S")}
        """.strip()
        self.send_message(message, silent=True)
