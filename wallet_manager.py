import json
import os
from typing import Optional, Tuple
import requests

class WalletManager:
    def __init__(self, wallet_path: str = "wallet.json", rpc_endpoint: str = "https://api.mainnet-beta.solana.com"):
        self.wallet_path = wallet_path
        self.rpc_endpoint = rpc_endpoint
        self.pubkey = None
        self.private_key = None
        self._load_wallet()

    def _load_wallet(self):
        """Load wallet from wallet.json"""
        if not os.path.exists(self.wallet_path):
            print(f"⚠️  {self.wallet_path} not found. Using fallback values.")
            self.pubkey = None
            return

        try:
            with open(self.wallet_path, 'r') as f:
                data = json.load(f)

            # Common formats support
            if isinstance(data, dict):
                self.pubkey = data.get("publicKey") or data.get("pubkey")
                self.private_key = data.get("privateKey") or data.get("secretKey")
            elif isinstance(data, list):
                # Sometimes wallet.json is just the private key array
                self.private_key = data
                print("📋 Loaded private key array from wallet.json")

            if self.pubkey:
                print(f"✅ Wallet loaded | Pubkey: {self.pubkey[:12]}...")
            else:
                print("✅ Wallet loaded (private key only)")

        except Exception as e:
            print(f"❌ Failed to load wallet.json: {e}")

    async def get_sol_balance(self) -> float:
        """Get real SOL balance from chain"""
        if not self.pubkey:
            return 50.0  # fallback

        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [self.pubkey]
            }
            resp = requests.post(self.rpc_endpoint, json=payload, timeout=10)
            data = resp.json()

            if "result" in data and "value" in data["result"]:
                balance_lamports = data["result"]["value"]
                sol_balance = balance_lamports / 1_000_000_000
                print(f"💰 Wallet SOL Balance: {sol_balance:.4f} SOL")
                return sol_balance
            return 50.0
        except Exception as e:
            print(f"⚠️ Could not fetch SOL balance: {e}")
            return 50.0  # fallback

    def get_total_trading_capital(self, default: float = 50.0) -> float:
        """Decide trading capital (can be improved later)"""
        # For now: use 80% of wallet balance or default
        # You can change logic here (e.g. fixed amount, percentage, etc.)
        return default
