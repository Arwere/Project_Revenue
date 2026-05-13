from dataclasses import dataclass, field
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class TokenConfig:
    address: str
    symbol: str
    name: str
    strategy_weights: Dict[str, float] = field(default_factory=lambda: {"trend": 0.35, "momentum": 0.30, "mean_reversion": 0.25, "volatility": 0.10})
    timeframes: Dict[str, int] = field(default_factory=lambda: {"trend": 120, "momentum": 60, "mean_reversion": 30, "volatility": 40})
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
    TAKE_PROFIT_LEVELS: list = field(default_factory=lambda: [0.30, 0.65, 1.20])

    JUPITER_SLIPPAGE_BPS: int = 80
    DRY_RUN: bool = True
    MAX_TRADE_AMOUNT_SOL: float = 2.0
    MIN_TRADE_AMOUNT_SOL: float = 0.15
    RPC_ENDPOINT: str = "https://api.mainnet-beta.solana.com"

    # Telegram Settings
    TELEGRAM_ENABLED: bool = False
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    TELEGRAM_STATUS_INTERVAL_MINUTES: int = 30

    WALLET_PATH: str = "wallet.json"

    TOKENS: Dict[str, TokenConfig] = field(default_factory=dict)


# Global config instance
config = GlobalConfig()

# ====================== YOUR 3 TOKENS ======================
config.TOKENS["MM"] = TokenConfig(
    address="Ax8PSfCXxmxb8C8kYTzN5CPpTe6PyeZfFf8rrXNCjupx",
    symbol="MM",
    name="Milk Money"
)

config.TOKENS["WHITEWHALE"] = TokenConfig(
    address="a3W4qutoEJA4232T2gwZUfgYJTetr96pU4SJMwppump",
    symbol="WHITEWHALE",
    name="White Whale"
)

config.TOKENS["TROLL"] = TokenConfig(
    address="5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2",
    symbol="TROLL",
    name="Troll"
)

print(f"✅ Loaded {len(config.TOKENS)} tokens for monitoring")
