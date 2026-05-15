import httpx
import json
import asyncio
from typing import Dict

class ClaudeBrain:
    def __init__(self):
        self.api_key = "aaron-onboarding-api-key"
        self.model = "claude-3-haiku-20240307"
        self.client = httpx.AsyncClient(timeout=20.0)

    async def get_decision(self, context: str) -> Dict:
        try:
            prompt = f"""
You are Poseidon, a professional Solana meme coin trading agent.
Analyze the following market data and make a clear trading decision.

{context}

Respond in valid JSON only with this exact format:
{{
  "action": "STRONG_BUY | BUY | HOLD | SELL",
  "final_score": 7.8,
  "suggested_capital_percent": 0.18,
  "tp": 0.145,
  "sl": -0.072,
  "reason": "Short explanation"
}}
"""

            response = await self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": 300,
                    "temperature": 0.4,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )

            data = response.json()
            text = data["content"][0]["text"]
            
            # Extract JSON from response
            start = text.find("{")
            end = text.rfind("}") + 1
            json_str = text[start:end]
            
            return json.loads(json_str)

        except Exception as e:
            print(f"Claude Error: {e}")
            # Fallback to safe decision
            return {
                "action": "HOLD",
                "final_score": 5.5,
                "suggested_capital_percent": 0.0,
                "tp": 0.0,
                "sl": 0.0,
                "reason": "Claude unavailable - fallback"
            }

claude = ClaudeBrain()
