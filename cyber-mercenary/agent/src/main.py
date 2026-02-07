"""
Cyber-Mercenary Agent - Main Entry Point

Autonomous AI security agent for Monad blockchain that:
1. Proactively scans for vulnerabilities
2. Generates signed warnings
3. Monetizes through bounty system
4. Handles reactive gigs
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Settings
from services.minimax import MiniMaxClient
from services.scanner import ContractScanner
from services.signer import SignatureManager
from services.notifier import NotificationService
from jobs.scanner_job import ScannerJob
from jobs.bounty_job import BountyJob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/agent.log"),
    ],
)
logger = logging.getLogger(__name__)


class CyberMercenary:
    """Main agent orchestrator"""

    def __init__(self, config: Settings):
        self.config = config
        self.running = False

        # Initialize services
        self.minimax = MiniMaxClient(config)
        self.scanner = ContractScanner(config)
        self.signer = SignatureManager(config)
        self.notifier = NotificationService(config)

        # Initialize jobs
        self.scanner_job = ScannerJob(self, config)
        self.bounty_job = BountyJob(self, config)

        logger.info(f"CyberMercenary initialized: {config.agent_name}")

    async def start(self):
        """Start the agent"""
        self.running = True
        logger.info("Starting CyberMercenary agent...")

        # Start background tasks
        tasks = [
            asyncio.create_task(self.scanner_job.run()),
            asyncio.create_task(self.bounty_job.run()),
        ]

        # Start API server
        from api.server import create_app
        app = create_app(self)
        import uvicorn

        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
        )
        server = uvicorn.Server(config)

        # Run everything
        await asyncio.gather(
            *tasks,
            server.serve(),
        )

    async def stop(self):
        """Stop the agent"""
        self.running = False
        logger.info("Stopping CyberMercenary agent...")

    async def analyze_contract(self, contract_address: str, chain_id: int):
        """Analyze a contract for vulnerabilities"""
        logger.info(f"Analyzing contract: {contract_address}")

        # Get contract code
        code = await self.scanner.get_contract_code(
            contract_address, chain_id
        )

        # Send to MiniMax for analysis
        analysis = await self.minimax.analyze_contract(code)

        # Generate signed warning if vulnerabilities found
        if analysis.vulnerabilities:
            warning = await self.minimax.generate_warning(
                analysis.vulnerabilities[0],
                contract_address,
            )
            signature = self.signer.sign_warning(warning)

            return {
                "analysis": analysis,
                "warning": warning,
                "signature": signature,
            }

        return {"analysis": analysis, "warning": None, "signature": None}

    async def submit_bounty_report(
        self, bounty_id: int, ipfs_hash: str, vulnerability
    ):
        """Submit a vulnerability report to a bounty"""
        logger.info(f"Submitting report for bounty: {bounty_id}")

        # Generate signature
        message = f"{bounty_id}:{ipfs_hash}"
        signature = self.signer.sign_message(message)

        # Submit to contract
        tx_hash = await self.scanner.submit_report(
            bounty_id, ipfs_hash, signature
        )

        return tx_hash


async def main():
    """Main entry point"""
    config = Settings()

    if not config.validate():
        logger.error("Invalid configuration. Please check .env file.")
        sys.exit(1)

    agent = CyberMercenary(config)

    try:
        await agent.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await agent.stop()
    except Exception as e:
        logger.error(f"Agent error: {e}")
        await agent.stop()
        raise


if __name__ == "__main__":
    asyncio.run(main())
