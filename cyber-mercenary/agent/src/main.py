#!/usr/bin/env python3
"""
Cyber-Mercenary Agent - Minimal Working Version
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Load .env file from project root
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# Check config
PRIVATE_KEY = os.environ.get("PRIVATE_KEY", "")
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")

if not PRIVATE_KEY:
    logger.error("❌ PRIVATE_KEY not set in .env")
    exit(1)

if not MINIMAX_API_KEY:
    logger.error("❌ MINIMAX_API_KEY not set in .env")  
    exit(1)

logger.info("✅ Configuration validated")
logger.info(f"📡 RPC: {os.environ.get('MONAD_RPC_URL', 'wss://monad-testnet.drpc.org')}")


async def main():
    """Main entry point"""
    logger.info("🚀 Cyber-Mercenary Agent Starting...")
    
    # Import services
    from api.server import app
    import uvicorn
    
    logger.info("🌐 Starting API server on port 8000...")
    
    # Start server
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
