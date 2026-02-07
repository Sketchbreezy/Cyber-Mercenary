"""
ECDSA Signature Manager

Handles signing of warnings and transactions for the agent.
"""

import logging
from typing import Optional
from dataclasses import dataclass
from eth_account import Account
from eth_account.messages import encode_structured_data
from eth_hash import keccak

from config import Settings

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

    def __init__(self, config: Settings):
        self.config = config
        self._account: Optional[Account] = None

    def _get_account(self) -> Account:
        """Get or create the signing account"""
        if self._account is None:
            if not self.config.blockchain.private_key:
                raise ValueError("Private key not configured")

            self._account = Account.from_key(
                self.config.blockchain.private_key
            )

            # Set agent address if not configured
            if not self.config.blockchain.agent_address:
                self.config.blockchain.agent_address = (
                    self._account.address
                )

        return self._account

    @property
    def address(self) -> str:
        """Get the agent's signing address"""
        return self._get_account().address

    def sign_message(self, message: str) -> SignedMessage:
        """
        Sign a message using ECDSA.

        Args:
            message: The message to sign

        Returns:
            SignedMessage with the signature
        """
        try:
            account = self._get_account()

            # Encode the message (EIP-191 standard)
            encoded = encode_structured_data(
                {"primaryType": "Message", "types": {"EIP712Domain": []}}
            )
            # For simple string messages
            from eth_account.messages import encode_defunct

            encoded = encode_defunct(text=message)

            signed = account.sign_message(encoded)

            return SignedMessage(
                message=message,
                signature=signed.signature.hex(),
                hash=keccak(text=message).hex(),
                signer_address=account.address,
            )

        except Exception as e:
            logger.error(f"Failed to sign message: {e}")
            raise

    def sign_warning(self, warning: str) -> SignedMessage:
        """
        Sign a security warning.

        Args:
            warning: The warning message

        Returns:
            SignedMessage with the signature
        """
        # Create a structured warning message
        structured_message = f"""CyberMercenary Security Warning
---
{warning}
---
Timestamp: {self._get_timestamp()}
Agent: {self.address}"""

        return self.sign_message(structured_message)

    def sign_transaction(self, transaction: dict) -> dict:
        """
        Sign an Ethereum transaction.

        Args:
            transaction: The transaction dictionary

        Returns:
            Signed transaction dictionary
        """
        try:
            account = self._get_account()

            # Add required fields
            transaction["nonce"] = transaction.get("nonce", 0)
            transaction["chainId"] = transaction.get(
                "chainId", self.config.blockchain.monad_chain_id
            )

            # Sign the transaction
            signed = account.sign_transaction(transaction)

            return {
                "rawTransaction": signed.rawTransaction.hex(),
                "hash": signed.hash.hex(),
                "r": hex(signed.r),
                "s": hex(signed.s),
                "v": signed.v,
            }

        except Exception as e:
            logger.error(f"Failed to sign transaction: {e}")
            raise

    def verify_signature(
        self, message: str, signature: str, expected_address: str
    ) -> bool:
        """
        Verify a signature.

        Args:
            message: The original message
            signature: The signature to verify
            expected_address: Expected signer address

        Returns:
            True if signature is valid
        """
        try:
            from eth_account import Account

            recovered = Account.recover_message(
                encode_defunct(text=message), signature=signature
            )
            return recovered.lower() == expected_address.lower()

        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False

    def get_domain_separator(self, name: str, version: str) -> bytes:
        """
        Get the EIP-712 domain separator.

        Args:
            name: Contract name
            version: Contract version

        Returns:
            Domain separator hash
        """
        return keccak(
            abi.encode(
                [
                    "bytes32",
                    "bytes32",
                    "bytes32",
                    "uint256",
                    "address",
                ],
                [
                    keccak(b"EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                    keccak(b"CyberMercenary"),
                    keccak(b"1"),
                    self.config.blockchain.monad_chain_id,
                    self.config.contracts.escrow or b"\x00" * 20,
                ],
            )
        )

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp"""
        from datetime import datetime

        return datetime.utcnow().isoformat()

    def create_delegation(
        self, delegate_address: str, expiration: int
    ) -> tuple[str, SignedMessage]:
        """
        Create a delegation signature.

        Args:
            delegate_address: Address to delegate to
            expiration: Expiration timestamp

        Returns:
            Tuple of (delegation data, signature)
        """
        delegation_data = {
            "delegate": delegate_address,
            "expiration": expiration,
            "nonce": 0,  # Would need to track nonces
        }

        message = f"""CyberMercenary Delegation
---
Delegate: {delegate_address}
Expires: {expiration}
Nonce: 0"""

        signature = self.sign_message(message)

        return delegation_data, signature
