import asyncio
import time
from config import config
from master import TradingSystem

async def run_supervisor():
    print("🔥 Starting Multi-Token Trading Supervisor")
    print(f"Monitoring {len(config.TOKENS)} tokens\n")
    
    # You can run multiple systems with different configs if needed
    system = TradingSystem()
    await system.run()

if __name__ == "__main__":
    asyncio.run(run_supervisor())
