"""
Scanner Job

Periodic contract scanning job for the Cyber-Mercenary agent.
"""

import asyncio
import logging
from typing import Optional

from config import Settings

logger = logging.getLogger(__name__)


class ScannerJob:
    """Handles periodic contract scanning"""

    def __init__(self, agent, config: Settings):
        # Lazy import to avoid circular import
        from main import CyberMercenary
        self.agent: CyberMercenary = agent
        self.config = config
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def run(self):
        """Run the scanner job"""
        logger.info("Scanner job started")
        self._running = True

        scan_interval = self.config.agent.scan_interval_minutes * 60

        while self._running:
            try:
                await self._scan_cycle()
            except Exception as e:
                logger.error(f"Scan cycle failed: {e}")

            # Wait for next interval
            await asyncio.sleep(scan_interval)

        logger.info("Scanner job stopped")

    async def _scan_cycle(self):
        """Execute a single scan cycle"""
        logger.info("Starting scan cycle")

        # Get current block
        block_number = self.agent.scanner.get_block_number()
        logger.info(f"Current block: {block_number}")

        # Scan recent contracts
        recent_contracts = await self.agent.scanner.scan_recent_contracts(100)

        for contract in recent_contracts:
            logger.info(f"Found contract: {contract}")
