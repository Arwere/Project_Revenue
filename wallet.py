import json
from pathlib import Path

def load_wallet():
    try:
        with open("wallet.json", "r") as f:
            wallet = json.load(f)
        print("✅ Wallet loaded successfully")
        return wallet
    except FileNotFoundError:
        print("❌ wallet.json not found!")
        return None
    except Exception as e:
        print(f"Error loading wallet: {e}")
        return None

def get_public_key(wallet):
    """Extract public key from wallet.json"""
    if isinstance(wallet, dict):
        return wallet.get("publicKey") or wallet.get("pubkey")
    return None
