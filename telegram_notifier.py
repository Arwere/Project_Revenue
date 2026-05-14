import asyncio
import time
import httpx

class TelegramNotifier:
    def __init__(self):
        self.token = "8662648328:AAF68vXslSCW6VIrna-NkPe7mnvMipp1-DY"
        self.chat_id = -1003770619404
        self.client = httpx.AsyncClient(timeout=10.0)

    async def send_message(self, message: str, topic_id: int):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "message_thread_id": topic_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            await self.client.post(url, json=payload)
        except Exception as e:
            print(f"Telegram error: {e}")

notifier = TelegramNotifier()
