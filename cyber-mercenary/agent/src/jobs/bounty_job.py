"""
Bounty Job

Handles bounty-related tasks for the Cyber-Mercenary agent.
"""

import asyncio
import logging
from typing import Optional

from config import Settings

logger = logging.getLogger(__name__)


class BountyJob:
    """Handles bounty operations"""

    def __init__(self, agent, config: Settings):
        # Lazy import to avoid circular import
        from main import CyberMercenary
        self.agent: CyberMercenary = agent
        self.config = config
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def run(self):
        """Run the bounty job"""
        logger.info("Bounty job started")
        self._running = True

        interval = self.config.agent.bounty_interval_minutes * 60

        while self._running:
            try:
                await self._bounty_cycle()
            except Exception as e:
                logger.error(f"Bounty cycle failed: {e}")

            await asyncio.sleep(interval)

        logger.info("Bounty job stopped")

    async def _bounty_cycle(self):
        """Execute a single bounty cycle"""
        logger.info("Starting bounty cycle")

        # Example logic: fetch active bounties
        active_bounties = await self.agent.bounty.fetch_active_bounties()
        for bounty in active_bounties:
            logger.info(f"Found bounty: {bounty}")
