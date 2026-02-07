"""
Scanner Job

Periodic contract scanning job for the Cyber-Mercenary agent.
"""

import asyncio
import logging
from typing import Optional

from config import Settings
from main import CyberMercenary

logger = logging.getLogger(__name__)


class ScannerJob:
    """Handles periodic contract scanning"""

    def __init__(self, agent: CyberMercenary, config: Settings):
        self.agent = agent
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
            if not contract.is_contract:
                continue

            logger.info(f"Scanning contract: {contract.address}")

            try:
                # Analyze contract
                result = await self.agent.analyze_contract(
                    contract.address, self.config.blockchain.monad_chain_id
                )

                # If vulnerabilities found, send warning
                if result.get("warning"):
                    await self.agent.notifier.send_warning(
                        result["warning"],
                        contract.address,
                        result["analysis"].vulnerabilities[0].severity,
                        result["signature"],
                    )

                # Log the scan
                logger.info(
                    f"Contract {contract.address}: "
                    f"{len(result['analysis'].vulnerabilities)} vulnerabilities"
                )

            except Exception as e:
                logger.error(f"Failed to scan {contract.address}: {e}")

        logger.info(f"Scan cycle complete: {len(recent_contracts)} contracts")

    async def stop(self):
        """Stop the scanner job"""
        logger.info("Stopping scanner job...")
        self._running = False

        if self._task:
            self._task.cancel()
            await self._task

    def trigger_now(self):
        """Trigger an immediate scan"""
        if self._running and not self._task.done():
            self._task = asyncio.create_task(self._scan_cycle())
