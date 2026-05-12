import pandas as pd
from backtesting import Backtest, Strategy
from config import config
from agent import TradingAgent

class MultiStackBacktest(Strategy):
    commission = 0.0030
    
    def init(self):
        self.agent = TradingAgent()
        self.token_config = list(config.TOKENS.values())[0]
        print(f"🚀 Backtesting {self.token_config.symbol} - Selective v3")

    def next(self):
        prices = list(self.data.Close)
        if len(prices) < config.MIN_DATA_POINTS + 50:   # Higher data requirement
            return

        current_price = prices[-1]

        market_data = {
            "price_sol": current_price,
            "usd_price": current_price * 140,
            "volume": 25000,
            "market_cap": 8000000
        }

        decision = self.agent.get_risk_adjusted_decision(
            token_config=self.token_config,
            market_data=market_data,
            prices=prices
        )

        action = decision.get("action", "HOLD")
        score = decision.get("final_score", 0)

        # === Very Selective Entry ===
        if not self.position and action == "BUY" and score >= 8.5:
            size_sol = decision.get("risk", {}).get("size_sol", 0.12)
            equity = self._broker.equity
            size_percent = min(0.18, size_sol / (equity * current_price) if current_price > 0 else 0.12)
            
            self.buy(size=size_percent)
            print(f"🟢 BUY  @ {current_price:.8f} | Score: {score:.1f}")

        # === Strong Exits ===
        elif self.position:
            if score <= 4.2 or action in ["SELL", "REDUCE"]:
                self.sell()
                print(f"🔴 EXIT (Weak) @ {current_price:.8f} | Score: {score:.1f}")
            elif score >= 9.3 and len(self.trades) > 0 and self.trades[-1].pl > 30:
                self.sell()
                print(f"🔴 TAKE PROFIT @ {current_price:.8f} | Score: {score:.1f}")


if __name__ == "__main__":
    df = pd.read_csv("historical_data.csv")
    df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 
                          'close': 'Close', 'volume': 'Volume'})
    
    if len(df) > 0:
        df.index = pd.date_range(start="2025-01-01", periods=len(df), freq="15min")

    print(f"Loaded {len(df)} candles | Range: {df.index[0]} → {df.index[-1]}\n")

    bt = Backtest(df, MultiStackBacktest, cash=3000, commission=0.0030, 
                  exclusive_orders=True, trade_on_close=True, finalize_trades=True)

    stats = bt.run()
    print("\n" + "="*95)
    print("BACKTEST RESULTS - Selective v3")
    print("="*95)
    print(stats)
