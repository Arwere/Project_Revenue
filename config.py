from dataclasses import dataclass
from typing import Dict

@dataclass
class TokenConfig:
    address: str
    symbol: str
    enabled: bool = True   # Easy on/off switch

class Config:
    TOKENS: Dict[str, TokenConfig] = {
        "MM": TokenConfig(
            address="Ax8PSfCXxmxb8C8kYTzN5CPpTe6PyeZfFf8rrXNCjupx",
            symbol="MM",
            enabled=True
        ),
        "WHITEWHALE": TokenConfig(
            address="a3W4qutoEJA4232T2gwZUfgYJTetr96pU4SJMwppump",
            symbol="WHITEWHALE",
            enabled=True
        ),
        "TROLL": TokenConfig(
            address="5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2",
            symbol="TROLL",
            enabled=True
        ),
        # Add new tokens here easily:
        # "NEWTOKEN": TokenConfig(address="...", symbol="NEW", enabled=False),
    }

    @classmethod
    def get_enabled_tokens(cls):
        return {k: v for k, v in cls.TOKENS.items() if v.enabled}

config = Config()
