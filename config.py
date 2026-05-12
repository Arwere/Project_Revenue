from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class TokenConfig:
    address: str
    symbol: str
    name: str
    strategy_weights: Optional[Dict[str, float]] = None
    timeframes: Optional[Dict[str, int]] = None
    max_position_size: float = 0.25
    risk_level: str = "medium"


@dataclass
class GlobalConfig:
    POLL_SECONDS: int = 12
    MAX_HISTORY_POINTS: int = 10000
    MIN_DATA_POINTS: int = 40
    DASHBOARD_WIDTH: int = 140
    AGENT_NAME: str = "Multi_Token_Agent"
    RISK_LEVEL: str = "medium"

    STRATEGY_WEIGHTS: Dict[str, float] = field(default_factory=lambda: {
        "trend": 0.35, "momentum": 0.30, 
        "mean_reversion": 0.25, "volatility": 0.10
    })
    
    TIMEFRAMES: Dict[str, int] = field(default_factory=lambda: {
        "trend": 120, "momentum": 60, 
        "mean_reversion": 30, "volatility": 40
    })

    BASE_CURRENCY: str = "SOL"
    DEFAULT_POSITION_SIZE: float = 0.12
    MAX_POSITION_SIZE: float = 0.25
    STOP_LOSS_PCT: float = -0.12
    TAKE_PROFIT_LEVELS: List[float] = field(default_factory=lambda: [0.30, 0.65, 1.20])

    JUPITER_SLIPPAGE_BPS: int = 80
    DRY_RUN: bool = True
    MAX_TRADE_AMOUNT_SOL: float = 2.0
    MIN_TRADE_AMOUNT_SOL: float = 0.15
    RPC_ENDPOINT: str = "https://api.mainnet-beta.solana.com"

    TELEGRAM_ENABLED: bool = True
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "8662648328:AAF68vXslSCW6VIrna-NkPe7mnvMipp1-DY")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "-1003770619404")

    WALLET_PATH: str = "wallet.json"

    TOKENS: Dict[str, TokenConfig] = field(default_factory=dict)


config = GlobalConfig()

# ====================== MULTI-TOKEN SETUP ======================
config.TOKENS["MM"] = TokenConfig(
    address="Ax8PSfCXxmxb8C8kYTzN5CPpTe6PyeZfFf8rrXNCjupx",
    symbol="MM",
    name="Milk Money"
)

config.TOKENS["TEST1"] = TokenConfig(
    address="Ax8PSfCXxmxb8C8kYTzN5CPpTe6PyeZfFf8rrXNCjupx",  # same for testing
    symbol="TEST1",
    name="Test Token 1",
    max_position_size=0.15
)

config.TOKENS["TEST2"] = TokenConfig(
    address="Ax8PSfCXxmxb8C8kYTzN5CPpTe6PyeZfFf8rrXNCjupx",
    symbol="TEST2",
    name="Test Token 2"
)

print(f"✅ Loaded {len(config.TOKENS)} tokens for monitoring")
