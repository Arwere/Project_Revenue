from dataclasses import dataclass, field
from typing import Dict, Optional, List
import time
from datetime import datetime

@dataclass
class Position:
    token_key: str
    symbol: str
    entry_price: float
    amount: float
    sol_invested: float
    entry_time: float
    tp_levels: List[float] = field(default_factory=lambda: [0.15, 0.35, 0.60])
    sl: float = -0.085
    status: str = "OPEN"
    exit_trades: List[Dict] = field(default_factory=list)

class Portfolio:
    def __init__(self, total_capital_sol: float = 50.0, wallet_manager=None):
        self.wallet_manager = wallet_manager
        self.total_capital_sol = total_capital_sol      # Base / fallback
        self.positions: Dict[str, Position] = {}
        self.realized_pnl = 0.0
        self.max_portfolio_risk_sol = total_capital_sol * 0.65

        # Auto-refresh capital from wallet if available
        if self.wallet_manager:
            self.refresh_capital()

    async def refresh_capital(self):
        """Update total capital from real wallet balance"""
        if self.wallet_manager:
            try:
                real_balance = await self.wallet_manager.get_sol_balance()
                if real_balance > 5.0:  # safety threshold
                    self.total_capital_sol = real_balance
                    self.max_portfolio_risk_sol = self.total_capital_sol * 0.65
                    print(f"💰 Portfolio capital updated from wallet: {self.total_capital_sol:.4f} SOL")
                else:
                    print(f"⚠️ Wallet balance too low ({real_balance:.4f} SOL), keeping previous capital.")
            except Exception as e:
                print(f"⚠️ Failed to refresh capital from wallet: {e}")

    def open_position(self, token_key: str, symbol: str, entry_price: float, 
                     sol_amount: float, token_amount: float) -> bool:
        if token_key in self.positions and self.positions[token_key].status == "OPEN":
            print(f"⚠️ Position already open for {symbol}")
            return False

        if self.get_total_exposure() + sol_amount > self.max_portfolio_risk_sol:
            print(f"⚠️ Portfolio risk limit reached ({self.max_portfolio_risk_sol:.2f} SOL max). Cannot open {symbol}")
            return False

        pos = Position(
            token_key=token_key,
            symbol=symbol,
            entry_price=entry_price,
            amount=token_amount,
            sol_invested=sol_amount,
            entry_time=time.time()
        )
        self.positions[token_key] = pos
        print(f"🟢 PORTFOLIO: Opened {symbol} | {sol_amount:.4f} SOL @ {entry_price:.8f}")
        return True

    def should_exit(self, token_key: str, current_price: float) -> Dict:
        if token_key not in self.positions:
            return {"action": "HOLD", "reason": "No position"}

        pos = self.positions[token_key]
        if pos.status != "OPEN":
            return {"action": "HOLD", "reason": "Not open"}

        pnl_pct = (current_price - pos.entry_price) / pos.entry_price

        # Stop Loss
        if pnl_pct <= pos.sl:
            return {"action": "SELL", "reason": "STOP LOSS", "percent": 1.0, "pnl_pct": pnl_pct}

        # Stepped Take Profit
        for i, tp in enumerate(pos.tp_levels):
            if pnl_pct >= tp and not any(e.get("level") == i for e in pos.exit_trades):
                sell_pct = 0.35 if i == 0 else 0.40 if i == 1 else 1.0
                return {
                    "action": "SELL",
                    "reason": f"TP{i+1}",
                    "percent": sell_pct,
                    "level": i,
                    "pnl_pct": pnl_pct
                }

        # Time-based exit
        if time.time() - pos.entry_time > 86400 and pnl_pct > 0.08:
            return {"action": "SELL", "reason": "TIME EXIT", "percent": 0.70, "pnl_pct": pnl_pct}

        return {"action": "HOLD", "reason": "No trigger", "pnl_pct": pnl_pct}

    def close_partial(self, token_key: str, percent: float, exit_price: float, reason: str):
        if token_key not in self.positions:
            return
        pos = self.positions[token_key]

        exit_amount = pos.amount * percent
        sol_received = exit_amount * exit_price
        pnl = sol_received - (pos.sol_invested * percent)

        self.realized_pnl += pnl

        pos.exit_trades.append({
            "time": datetime.now().isoformat(),
            "percent": percent,
            "price": exit_price,
            "sol_received": sol_received,
            "pnl": pnl,
            "reason": reason
        })

        pos.amount -= exit_amount

        if pos.amount < 0.00001:
            pos.status = "CLOSED"
            print(f"🔴 FULLY CLOSED {pos.symbol} | PnL: {pnl:+.4f} SOL")
        else:
            print(f"🔴 PARTIAL CLOSE {pos.symbol} — {percent*100:.0f}% @ {exit_price:.8f} | {reason}")

    def get_position(self, token_key: str) -> Optional[Position]:
        return self.positions.get(token_key)

    def get_all_positions(self) -> Dict:
        return self.positions

    def get_total_exposure(self) -> float:
        return sum(p.sol_invested for p in self.positions.values() if p.status == "OPEN")

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> Dict:
        unrealized_pnl = 0.0
        total_value = 0.0

        for token_key, pos in self.positions.items():
            if pos.status == "OPEN" and token_key in current_prices:
                current_value = pos.amount * current_prices[token_key]
                unrealized_pnl += current_value - pos.sol_invested
                total_value += current_value

        total_pnl = self.realized_pnl + unrealized_pnl
        return {
            "total_capital": self.total_capital_sol,
            "deployed": self.get_total_exposure(),
            "available": self.total_capital_sol - self.get_total_exposure(),
            "current_value": self.total_capital_sol + total_pnl,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "total_pnl": total_pnl,
            "total_pnl_pct": (total_pnl / self.total_capital_sol) * 100 if self.total_capital_sol > 0 else 0
        }

    def get_summary(self) -> str:
        deployed = self.get_total_exposure()
        return (f"🌊 Moon Tide Portfolio | Capital: {self.total_capital_sol:.4f} SOL\n"
                f"Deployed: {deployed:.4f} SOL ({deployed/self.total_capital_sol*100:.1f}%) | "
                f"Realized PnL: {self.realized_pnl:+.4f} SOL")
