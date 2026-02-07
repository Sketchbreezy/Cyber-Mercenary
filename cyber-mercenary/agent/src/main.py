"""
Cyber-Mercenary Agent - Minimal Working Version
"""

import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Simple config - just read .env directly
def getenv(key, default=""):
    return os.environ.get(key, default)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Check config
PRIVATE_KEY = getenv("PRIVATE_KEY")
MINIMAX_API_KEY = getenv("MINIMAX_API_KEY")

if not PRIVATE_KEY:
    logger.error("❌ PRIVATE_KEY not set in .env")
    exit(1)

if not MINIMAX_API_KEY:
    logger.error("❌ MINIMAX_API_KEY not set in .env")  
    exit(1)

logger.info("✅ Configuration validated")


async def main():
    """Main entry point"""
    logger.info("🚀 Cyber-Mercenary Agent Starting...")
    logger.info(f"📡 RPC: {getenv('MONAD_RPC_URL', 'wss://monad-testnet.drpc.org')}")
    logger.info(f"🔗 Chain ID: {getenv('MONAD_CHAIN_ID', '10143')}")
    
    # Import services
    from api.server import app
    import uvicorn
    
    # Set up agent reference for API
    from api.server import _agent as api_agent
    api_agent._agent = None  # Will be set when we have full agent
    
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
