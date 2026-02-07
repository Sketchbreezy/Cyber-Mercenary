"""
Contract Scanner Service

Handles blockchain interaction for contract scanning and analysis.
"""

import logging
from typing import Optional
from dataclasses import dataclass

from web3 import Web3
from web3.providers import WebSocketProvider

from config import Settings

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Contract scan result"""
    address: str
    bytecode: str
    source_code: Optional[str]
    abi: Optional[list]
    is_contract: bool
    bytecode_hash: str


class ContractScanner:
    """Scans and analyzes contracts on the blockchain"""

    def __init__(self, config: Settings):
        self.config = config
        self.w3 = Web3(WebsocketProvider(config.blockchain.monad_rpc_url))

        # Cache for scanned contracts
        self._cache = {}

    def is_connected(self) -> bool:
        """Check blockchain connection"""
        return self.w3.is_connected()

    def get_block_number(self) -> int:
        """Get current block number"""
        return self.w3.eth.block_number

    async def get_contract_code(
        self, address: str, chain_id: int = 10143
    ) -> str:
        """
        Get the bytecode of a contract.

        Args:
            address: Contract address
            chain_id: Blockchain chain ID

        Returns:
            Contract bytecode as hex string
        """
        if address in self._cache:
            return self._cache[address]

        try:
            checksum_address = Web3.to_checksum_address(address)
            code = self.w3.eth.get_code(checksum_address).hex()

            self._cache[address] = code
            return code

        except Exception as e:
            logger.error(f"Failed to get contract code: {e}")
            return ""

    async def get_contract_creation_tx(self, address: str) -> Optional[dict]:
        """Get the creation transaction for a contract"""
        try:
            checksum_address = Web3.to_checksum_address(address)
            tx = self.w3.eth.get_transaction(
                self.w3.eth.get_code(checksum_address).transaction_index
            )
            return {
                "from": tx["from"],
                "data": tx["data"],
                "hash": tx["hash"].hex(),
            }
        except Exception as e:
            logger.error(f"Failed to get creation tx: {e}")
            return None

    async def get_contract_metadata(
        self, address: str
    ) -> Optional[dict]:
        """
        Get contract metadata (if available via EIP-3668).

        This is a placeholder - real implementation would need
        access to Sourcify or similar service.
        """
        try:
            checksum_address = Web3.to_checksum_address(address)
            # Check if this looks like a contract
            code = await self.get_contract_code(address)

            if code == "0x":
                return None

            return {
                "address": address,
                "bytecode_length": len(code) // 2 - 1,
                "is_contract": True,
            }
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            return None

    async def scan_address(
        self, address: str, chain_id: int = 10143
    ) -> ScanResult:
        """
        Perform a complete scan of an address.

        Args:
            address: Contract address
            chain_id: Blockchain chain ID

        Returns:
            ScanResult with all findings
        """
        logger.info(f"Scanning contract: {address}")

        bytecode = await self.get_contract_code(address, chain_id)
        is_contract = bytecode != "0x" and len(bytecode) > 2

        result = ScanResult(
            address=address,
            bytecode=bytecode,
            source_code=None,  # Would need Sourcify lookup
            abi=None,
            is_contract=is_contract,
            bytecode_hash=self.w3.keccak(hexstr=bytecode).hex()
            if bytecode
            else "",
        )

        return result

    async def scan_recent_contracts(
        self, block_range: int = 100
    ) -> list[ScanResult]:
        """
        Scan recently deployed contracts.

        Args:
            block_range: Number of blocks to scan

        Returns:
            List of ScanResult for new contracts
        """
        current_block = self.get_block_number()
        start_block = current_block - block_range

        results = []

        # This is simplified - real implementation would:
        # 1. Get all contract creations in the block range
        # 2. Batch fetch bytecode
        # 3. Filter for newly deployed contracts

        logger.info(f"Scanning blocks {start_block} to {current_block}")

        # Placeholder: return empty list
        return results

    async def submit_report(
        self, bounty_id: int, ipfs_hash: str, signature: str
    ) -> str:
        """
        Submit a vulnerability report to a bounty contract.

        Args:
            bounty_id: The bounty ID
            ipfs_hash: IPFS hash of the encrypted report
            signature: Agent's ECDSA signature

        Returns:
            Transaction hash
        """
        # This would interact with the deployed Escrow contract
        # For now, return a placeholder
        logger.info(f"Would submit report for bounty {bounty_id}")
        return "0xplaceholder"

    async def create_bounty(
        self, amount_wei: int, ipfs_hash: str, expires_in: int
    ) -> tuple[int, str]:
        """
        Create a new bounty.

        Args:
            amount_wei: Bounty amount in wei
            ipfs_hash: IPFS hash of report template
            expires_in: Time until expiry (seconds)

        Returns:
            Tuple of (bounty_id, transaction_hash)
        """
        logger.info(f"Creating bounty: {amount_wei} wei")
        # This would interact with the deployed Escrow contract
        return (1, "0xplaceholder")

    async def check_bounty_status(self, bounty_id: int) -> dict:
        """
        Check the status of a bounty.

        Args:
            bounty_id: The bounty ID

        Returns:
            Bounty status dictionary
        """
        # This would query the deployed Escrow contract
        return {
            "id": bounty_id,
            "claimed": False,
            "disputed": False,
            "expires_at": 0,
        }
