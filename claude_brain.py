import os
from anthropic import AsyncAnthropic
import json

class ClaudeBrain:
    def __init__(self):
        self.client = AsyncAnthropic(api_key="aaron-onboarding-api-key")
        self.system_prompt = """You are Poseidon, a highly disciplined Solana meme coin trading AI.
You prioritize capital preservation above all.
You are cautious with high-volatility tokens.
You combine technical data with market intuition.
Always output valid JSON only."""

    async def get_decision(self, market_context: dict) -> dict:
        prompt = f"""
Token: {market_context.get('symbol', 'Unknown')}
Current Price: {market_context.get('price', 0):.8f} SOL
Technical Score: {market_context.get('tech_score', 0):.1f}
Recent Trend: {market_context.get('price_trend', 'Neutral')}
RSI: {market_context.get('rsi', 'N/A')}
MACD Hist: {market_context.get('macd_hist', 'N/A')}
Volatility: {market_context.get('volatility', 'N/A')}

Analyze the situation and respond with valid JSON only:
{{
  "action": "STRONG_BUY | BUY | HOLD | SELL | AVOID",
  "confidence": 0.0 to 1.0,
  "suggested_capital_percent": 0.0 to 1.0,
  "reason": "short reasoning"
}}
"""

        try:
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                temperature=0.3,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text.strip()
            decision = json.loads(text)
            return decision

        except Exception as e:
            print(f"Claude API Error: {e}")
            return {
                "action": "HOLD",
                "confidence": 0.5,
                "suggested_capital_percent": 0.0,
                "reason": "Claude unavailable - fallback to HOLD"
            }

# Global instance
claude = ClaudeBrain()
