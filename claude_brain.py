import httpx
import json
import asyncio
from typing import Dict, List
import time

class ClaudeBrain:
    def __init__(self):
        self.api_key = "aaron-onboarding-api-key"
        self.model = "claude-3-haiku-20240307"
        self.client = httpx.AsyncClient(timeout=25.0)
        self.memory = []  # Short-term memory of recent trades/decisions
        self.max_memory = 8

    def add_to_memory(self, token_symbol: str, action: str, score: float, reason: str):
        self.memory.append({
            "time": time.strftime("%H:%M"),
            "token": token_symbol,
            "action": action,
            "score": score,
            "reason": reason[:80]
        })
        if len(self.memory) > self.max_memory:
            self.memory.pop(0)

    async def get_decision(self, context: str) -> Dict:
        memory_context = "\n".join([f"{m['time']} {m['token']}: {m['action']} (score {m['score']}) - {m['reason']}" for m in self.memory[-5:]])

        prompt = f"""
You are Poseidon, an elite Solana meme coin trading agent.

Recent Memory:
{memory_context if memory_context else "No previous trades yet."}

Current Market Data:
{context}

Make a decisive trading recommendation. Respond with **valid JSON only** in this exact format:
{{
  "action": "STRONG_BUY | BUY | HOLD | SELL",
  "final_score": 7.8,
  "suggested_capital_percent": 0.15,
  "tp": 0.14,
  "sl": -0.07,
  "reason": "One short clear reason"
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

            # Better parsing
            if "content" in data and len(data["content"]) > 0:
                text = data["content"][0]["text"]
            else:
                raise ValueError("No content in response")

            # Extract JSON
            start = text.find("{")
            end = text.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found")

            json_str = text[start:end]
            result = json.loads(json_str)

            # Add to memory
            self.add_to_memory(
                context.split("Token: ")[1].split("\n")[0] if "Token:" in context else "Unknown",
                result.get("action", "HOLD"),
                result.get("final_score", 5.0),
                result.get("reason", "")
            )

            return result

        except Exception as e:
            print(f"Claude Error: {e}")
            return {
                "action": "HOLD",
                "final_score": 5.5,
                "suggested_capital_percent": 0.0,
                "tp": 0.0,
                "sl": 0.0,
                "reason": "Claude fallback - using technical rules"
            }

claude = ClaudeBrain()
