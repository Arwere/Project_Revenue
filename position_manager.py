from dataclasses import dataclass, field
from typing import Dict, Optional, List
import time
from datetime import datetime

@dataclass
class Position:
    token_key: str
    symbol: str
    entry_price: float
    amount: float          # tokens held
    sol_invested: float
    entry_time: float
    tp_levels: List[float] = field(default_factory=lambda: [0.15, 0.35, 0.60])
    sl: float = -0.085
    status: str = "OPEN"
    exit_trades: List[Dict] = field(default_factory=list)

class PositionManager:
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.total_sol_invested = 0.0
        self.max_portfolio_risk_sol = 15.0  # safety cap - adjust as needed

    def open_position(self, token_key: str, symbol: str, entry_price: float, 
                     sol_amount: float, token_amount: float) -> bool:
        if token_key in self.positions and self.positions[token_key].status == "OPEN":
            print(f"⚠️ Position already open for {symbol}")
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
        self.total_sol_invested += sol_amount
        print(f"🟢 POSITION OPENED → {symbol} | {sol_amount:.4f} SOL @ {entry_price:.8f}")
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

        # Time-based exit (24h+ with profit)
        if time.time() - pos.entry_time > 86400 and pnl_pct > 0.08:
            return {"action": "SELL", "reason": "TIME EXIT", "percent": 0.70, "pnl_pct": pnl_pct}

        return {"action": "HOLD", "reason": "No trigger", "pnl_pct": pnl_pct}

    def close_partial(self, token_key: str, percent: float, exit_price: float, reason: str):
        if token_key not in self.positions:
            return
        pos = self.positions[token_key]
        exit_amount = pos.amount * percent
        sol_received = exit_amount * exit_price

        pos.exit_trades.append({
            "time": datetime.now().isoformat(),
            "percent": percent,
            "price": exit_price,
            "sol": sol_received,
            "reason": reason
        })

        pos.amount -= exit_amount
        if pos.amount < 0.00001:
            pos.status = "CLOSED"
            print(f"🔴 FULLY CLOSED {pos.symbol}")
        else:
            print(f"🔴 PARTIAL CLOSE {pos.symbol} — {percent*100:.0f}% @ {exit_price:.8f} | Reason: {reason}")

    def get_position(self, token_key: str) -> Optional[Position]:
        return self.positions.get(token_key)

    def get_all_positions(self) -> Dict:
        return self.positions
