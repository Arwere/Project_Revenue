import pandas as pd
import asyncio
from datetime import datetime
from agent import TradingAgent
from config import config
from data_fetcher import get_historical_prices
from risk_manager import RiskManager


class MultiTokenBacktester:
    def __init__(self):
        self.agent = TradingAgent()
        self.risk_manager = RiskManager()

    async def backtest_token(self, token_key: str, days: int = 30):
        token_config = config.TOKENS[token_key]
        symbol = token_config.symbol
        address = token_config.address

        print(f"\n🔍 Backtesting {symbol} ({address[:12]}...)")

        prices = await get_historical_prices(address, limit=days * 96)
        if len(prices) < 300:
            print(f"❌ Not enough data for {symbol}")
            return None

        df = pd.DataFrame({"close": prices})
        df['timestamp'] = pd.date_range(end=datetime.now(), periods=len(df), freq='15min')

        equity = 1000.0
        position = 0.0
        entry_price = 0.0
        trades = 0
        wins = 0

        print(f"   Testing {len(df)} candles...")

        for i in range(150, len(df)):
            current_prices = df['close'].iloc[:i].tolist()
            current_price = df['close'].iloc[i]

            market_data = {"price_sol": current_price, "usd_price": current_price * 95}

            decision = self.agent.get_risk_adjusted_decision(
                token_config=token_config,
                market_data=market_data,
                prices=current_prices
            )

            action = decision.get("action", "HOLD")
            score = decision.get("final_score", 0)

            if action in ["BUY", "STRONG_BUY"] and position == 0 and score >= 6.8:
                position = equity * 0.8 / current_price
                entry_price = current_price
                trades += 1
                print(f"   BUY  {symbol} @ {current_price:.8f} | Score: {score:.1f}")

            elif position > 0:
                pnl = (current_price - entry_price) / entry_price
                if pnl >= 0.22 or pnl <= -0.13:   # TP or SL
                    equity += position * current_price * 0.995
                    position = 0
                    if pnl > 0:
                        wins += 1
                    print(f"   EXIT {symbol} @ {current_price:.8f} | PnL: {pnl*100:+.1f}%")

        win_rate = (wins / trades * 100) if trades > 0 else 0
        total_return = (equity - 1000) / 1000 * 100

        print(f"\n=== {symbol} RESULTS ===")
        print(f"Final Equity : ${equity:,.2f}")
        print(f"Return       : {total_return:+.2f}%")
        print(f"Trades       : {trades}")
        print(f"Win Rate     : {win_rate:.1f}%")
        print("="*50)

        return {
            "symbol": symbol,
            "return": total_return,
            "trades": trades,
            "win_rate": win_rate
        }

    async def run_all(self):
        print("🚀 Starting Multi-Token Backtest...\n")
        results = []

        for token_key in config.TOKENS.keys():
            result = await self.backtest_token(token_key, days=30)
            if result:
                results.append(result)

        # Portfolio Summary
        if results:
            avg_return = sum(r["return"] for r in results) / len(results)
            print(f"\n📊 MULTI-TOKEN SUMMARY")
            print(f"Average Return : {avg_return:+.2f}%")
            print(f"Tokens Tested  : {len(results)}")


if __name__ == "__main__":
    bt = MultiTokenBacktester()
    asyncio.run(bt.run_all())
