"""
Notification Service

Handles delivery of security warnings and notifications.
"""

import logging
from typing import Optional
from dataclasses import dataclass
from enum import Enum

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Settings

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Available notification channels"""
    TELEGRAM = "telegram"
    EMAIL = "email"
    WEBHOOK = "webhook"
    IPFS = "ipfs"
    ONCHAIN = "onchain"


@dataclass
class Notification:
    """A notification to be sent"""
    channel: NotificationChannel
    recipient: str
    subject: Optional[str]
    body: str
    priority: str = "normal"  # low, normal, high, critical
    metadata: Optional[dict] = None


class NotificationService:
    """Sends notifications through various channels"""

    def __init__(self, config: Settings):
        self.config = config
        self._channels = {}

    async def send_warning(
        self,
        warning: str,
        contract_address: str,
        severity: str,
        signature: str,
    ) -> bool:
        """
        Send a security warning notification.

        Args:
            warning: Warning message
            contract_address: Vulnerable contract address
            severity: Severity level
            signature: ECDSA signature

        Returns:
            True if sent successfully
        """
        logger.info(f"Sending {severity} warning for {contract_address}")

        # In a real implementation, this would:
        # 1. Store warning to IPFS
        # 2. Send notification via configured channels
        # 3. Emit on-chain event

        notification = Notification(
            channel=NotificationChannel.TELEGRAM,
            recipient=self.config.agent.name,  # Would be user's Telegram
            subject=f"[{severity.upper()}] Security Warning",
            body=f"{warning}\n\nContract: {contract_address}\nSignature: {signature[:20]}...",
            priority=severity,
            metadata={
                "contract": contract_address,
                "severity": severity,
                "signature": signature,
            },
        )

        return await self._send(notification)

    async def send_bounty_alert(
        self, bounty_id: int, developer: str, amount: str
    ) -> bool:
        """Send bounty creation alert"""
        logger.info(f"Bounty {bounty_id} created by {developer}")

        notification = Notification(
            channel=NotificationChannel.TELEGRAM,
            recipient=self.config.agent.name,
            subject="New Bounty Created",
            body=f"New bounty #{bounty_id}\nDeveloper: {developer}\nAmount: {amount}",
            priority="normal",
            metadata={"bounty_id": bounty_id},
        )

        return await self._send(notification)

    async def send_gig_notification(
        self, gig_id: int, task_type: str, fee: str
    ) -> bool:
        """Send gig marketplace notification"""
        logger.info(f"New gig {gig_id}: {task_type} for {fee}")

        notification = Notification(
            channel=NotificationChannel.TELEGRAM,
            recipient=self.config.agent.name,
            subject="New Gig Available",
            body=f"Gig #{gig_id}\nTask: {task_type}\nFee: {fee}",
            priority="normal",
            metadata={"gig_id": gig_id, "task_type": task_type},
        )

        return await self._send(notification)

    async def _send(self, notification: Notification) -> bool:
        """
        Send a notification through the appropriate channel.

        Args:
            notification: The notification to send

        Returns:
            True if sent successfully
        """
        try:
            if notification.channel == NotificationChannel.TELEGRAM:
                return await self._send_telegram(notification)
            elif notification.channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(notification)
            elif notification.channel == NotificationChannel.IPFS:
                return await self._store_ipfs(notification)
            else:
                logger.warning(f"Unsupported channel: {notification.channel}")
                return False

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    async def _send_telegram(self, notification: Notification) -> bool:
        """
        Send notification via Telegram.

        This is a placeholder - real implementation would use
        the Telegram Bot API.
        """
        logger.info(
            f"[TELEGRAM] To {notification.recipient}: {notification.subject}"
        )
        return True

    async def _send_webhook(self, notification: Notification) -> bool:
        """
        Send notification via webhook.

        This is a placeholder - real implementation would make
        an HTTP POST request.
        """
        logger.info(
            f"[WEBHOOK] To {notification.recipient}: {notification.subject}"
        )
        return True

    async def _store_ipfs(self, notification: Notification) -> bool:
        """
        Store notification to IPFS.

        This is a placeholder - real implementation would upload
        to IPFS and return the CID.
        """
        logger.info(
            f"[IPFS] Storing: {notification.subject}"
        )
        return True

    async def broadcast_alert(
        self,
        title: str,
        message: str,
        severity: str = "normal",
        affected_contracts: list[str] = None,
    ) -> int:
        """
        Broadcast an alert across all channels.

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
            affected_contracts: List of affected contract addresses

        Returns:
            Number of notifications sent
        """
        count = 0

        if affected_contracts is None:
            affected_contracts = []

        notification = Notification(
            channel=NotificationChannel.TELEGRAM,
            recipient=self.config.agent.name,
            subject=title,
            body=message,
            priority=severity,
            metadata={"contracts": affected_contracts},
        )

        if await self._send_telegram(notification):
            count += 1

        if await self._send_webhook(notification):
            count += 1

        if await self._store_ipfs(notification):
            count += 1

        return count
