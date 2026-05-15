import httpx
import json
import time
from typing import Dict

class ClaudeBrain:
    def __init__(self):
        self.api_key = "aaron-onboarding-api-key"
        self.model = "claude-3-haiku-20240307"
        self.client = httpx.AsyncClient(timeout=25.0)
        self.telegram_token = "8662648328:AAF68vXslSCW6VIrna-NkPe7mnvMipp1-DY"
        self.chat_id = -1003770619404
        self.claude_topic_id = 135   # ← Claude Haiku topic
        self.memory = []

    def add_to_memory(self, token: str, action: str, score: float, reason: str):
        self.memory.append({
            "time": time.strftime("%H:%M"),
            "token": token,
            "action": action,
            "score": score,
            "reason": reason
        })
        if len(self.memory) > 10:
            self.memory.pop(0)

    async def send_to_telegram(self, message: str):
        """Send Claude's decision to Topic 135"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "message_thread_id": self.claude_topic_id,
                "text": message,
                "parse_mode": "HTML"
            }
            await httpx.AsyncClient().post(url, json=payload)
        except Exception as e:
            print(f"Telegram send error: {e}")

    async def get_decision(self, context: str) -> Dict:
        memory_text = "\n".join([f"{m['time']} | {m['token']}: {m['action']} ({m['score']}) → {m['reason']}" 
                               for m in self.memory[-6:]])

        prompt = f"""You are Poseidon, a sharp Solana meme coin trading agent.

Recent Memory:
{memory_text if memory_text else "No previous trades."}

Current Data:
{context}

Respond **ONLY** with valid JSON in this exact format:

{{
  "action": "STRONG_BUY | BUY | HOLD | SELL",
  "final_score": 8.2,
  "suggested_capital_percent": 0.18,
  "tp": 0.145,
  "sl": -0.072,
  "reason": "Short clear professional reason (max 120 chars)"
}}
"""

        try:
            response = await self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": 400,
                    "temperature": 0.35,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )

            data = response.json()
            text = data["content"][0]["text"]

            start = text.find("{")
            end = text.rfind("}") + 1
            result = json.loads(text[start:end])

            # Add to memory
            token_name = context.split("Token: ")[1].split("\n")[0] if "Token:" in context else "Unknown"
            self.add_to_memory(token_name, result.get("action"), result.get("final_score", 5.5), result.get("reason", ""))

            # Send to Claude Topic (135)
            msg = f"<b>🤖 POSEIDON (Claude)</b>\n\n" \
                  f"Token: {token_name}\n" \
                  f"Action: <b>{result.get('action')}</b>\n" \
                  f"Score: {result.get('final_score')}\n" \
                  f"Capital: {result.get('suggested_capital_percent', 0)*100:.1f}%\n" \
                  f"TP: +{result.get('tp')*100:.1f}% | SL: {result.get('sl')*100:.1f}%\n" \
                  f"Reason: {result.get('reason')}"

            await self.send_to_telegram(msg)

            return result

        except Exception as e:
            print(f"Claude Error: {e}")
            return {
                "action": "HOLD",
                "final_score": 5.5,
                "suggested_capital_percent": 0.0,
                "tp": 0.0,
                "sl": 0.0,
                "reason": "Error - fallback"
            }

claude = ClaudeBrain()
