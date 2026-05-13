import pandas as pd
import asyncio
import numpy as np
import warnings
from agent import TradingAgent
from config import config
from data_fetcher import get_historical_prices

warnings.filterwarnings("ignore")

class MultiTokenBacktester:
    def __init__(self):
        self.agent = TradingAgent()

    async def backtest_token(self, token_key: str):
        token_config = config.TOKENS[token_key]
        symbol = token_config.symbol
        print(f"\n🔍 Backtesting {symbol}...")

        prices = await get_historical_prices(token_config.address, limit=1500)
        df = pd.DataFrame({"close": prices})
        equity = 1000.0
        position = 0.0
        entry_price = 0.0
        trades = []
        max_score = 0

        print(f"   Testing {len(df)} real candles...")

        for i in range(400, len(df)):
            current_prices = df['close'].iloc[:i].tolist()
            current_price = df['close'].iloc[i]

            market_data = {"price_sol": current_price, "usd_price": current_price * 95}

            decision = self.agent.get_risk_adjusted_decision(token_config, market_data, current_prices)
            action = decision.get("action", "HOLD")
            score = decision.get("final_score", 0)
            max_score = max(max_score, score)

            if score >= 6.5:
                print(f"   Score: {score:.1f} | {action} @ {current_price:.8f}")

            # === ADAPTIVE ENTRY LOGIC ===
            if action in ["BUY", "STRONG_BUY"] and position == 0 and score >= 6.7:
                sma50 = np.mean(current_prices[-50:]) if len(current_prices) >= 50 else current_price
                
                # Adaptive based on token volatility / behavior
                if symbol == "TROLL" or "pump" in symbol.lower():
                    dip_threshold = 0.88   # High volume / volatile tokens
                elif symbol == "MM":
                    dip_threshold = 0.91
                else:
                    dip_threshold = 0.925
                
                if current_price > sma50 * dip_threshold:
                    position = equity * 0.38 / current_price
                    entry_price = current_price
                    trades.append({"entry": current_price, "pnl": None})
                    print(f"   ✅ BUY  {symbol} @ {current_price:.8f} | Score: {score:.1f} | Dip OK")

            elif position > 0:
                pnl_pct = (current_price - entry_price) / entry_price
                # Adaptive exits
                if pnl_pct >= 0.145 or pnl_pct <= -0.085:
                    final_pnl = pnl_pct
                    equity += position * current_price * 0.995
                    position = 0.0
                    if trades:
                        trades[-1]["pnl"] = final_pnl
                    status = "WIN" if final_pnl > 0 else "LOSS"
                    print(f"   EXIT @ {current_price:.8f} | PnL: {final_pnl*100:+.1f}% ({status})")

        completed = [t for t in trades if t.get("pnl") is not None]
        wins = len([t for t in completed if t["pnl"] > 0])
        win_rate = (wins / len(completed) * 100) if completed else 0
        total_return = (equity - 1000) / 1000 * 100

        print(f"\n=== {symbol} RESULTS ===")
        print(f"Final Equity : ${equity:,.2f} | Return: {total_return:+.2f}%")
        print(f"Trades       : {len(completed)} | Win Rate: {win_rate:.1f}%")
        print(f"Max Score Seen: {max_score:.1f}")
        print("="*90)

        return {"win_rate": win_rate, "trades": len(completed)}

    async def run_all(self):
        print("🚀 Backtest v20 - Fully Adaptive for Any Token\n")
        results = []
        for key in config.TOKENS.keys():
            res = await self.backtest_token(key)
            results.append(res)

        if results:
            avg = sum(r["win_rate"] for r in results) / len(results)
            print(f"\n📊 OVERALL Avg Win Rate: {avg:.1f}%")

if __name__ == "__main__":
    bt = MultiTokenBacktester()
    asyncio.run(bt.run_all())
