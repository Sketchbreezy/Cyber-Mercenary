"""
ECDSA Signature Manager

Handles signing of warnings and transactions for the agent.
"""

import logging
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3

logger = logging.getLogger(__name__)


@dataclass
class SignedMessage:
    """A signed message with its signature"""
    message: str
    signature: str
    hash: str
    signer_address: str


class SignatureManager:
    """Manages ECDSA signatures for the agent"""

    def __init__(self, config):
        self.config = config
        self._account: Optional[Account] = None

    def _get_account(self) -> Account:
        """Get or create the signing account"""
        if self._account is None:
            if not self.config.blockchain.private_key:
                raise ValueError("Private key not configured")

            self._account = Account.from_key(self.config.blockchain.private_key)

            # Set agent address if not configured
            if not self.config.blockchain.agent_address:
                self.config.blockchain.agent_address = self._account.address

        return self._account

    @property
    def address(self) -> str:
        """Get the agent's signing address"""
        return self._get_account().address

    def sign_message(self, message: str) -> SignedMessage:
        """Sign a message using ECDSA."""
        try:
            account = self._get_account()
            encoded = encode_defunct(text=message)
            signed = account.sign_message(encoded)

            # Use web3 for keccak hash
            hash_bytes = Web3.keccak(text=message)

            return SignedMessage(
                message=message,
                signature=signed.signature.hex(),
                hash=hash_bytes.hex(),
                signer_address=account.address,
            )
        except Exception as e:
            logger.error(f"Failed to sign message: {e}")
            raise

    def sign_warning(self, warning: str) -> SignedMessage:
        """Sign a security warning."""
        structured_message = f"""CyberMercenary Security Warning
---
{warning}
---
Timestamp: {datetime.utcnow().isoformat()}
Agent: {self.address}"""

        return self.sign_message(structured_message)

    def verify_signature(self, message: str, signature: str, expected_address: str) -> bool:
        """Verify a signature."""
        try:
            recovered = Account.recover_message(
                encode_defunct(text=message), signature=signature
            )
            return recovered.lower() == expected_address.lower()
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False

    def create_delegation(self, delegate_address: str, expiration: int) -> tuple[dict, SignedMessage]:
        """Create a delegation signature."""
        delegation_data = {
            "delegate": delegate_address,
            "expiration": expiration,
            "nonce": 0,
        }

        message = f"""CyberMercenary Delegation
---
Delegate: {delegate_address}
Expires: {expiration}
Nonce: 0"""

        signature = self.sign_message(message)
        return delegation_data, signature
