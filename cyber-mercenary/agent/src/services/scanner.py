"""
Contract Scanner Service

Handles blockchain interaction for contract scanning and analysis.
"""

import logging
from typing import Optional
from dataclasses import dataclass

from web3 import Web3

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

    def __init__(self, config):
        self.config = config
        self.w3 = Web3(Web3.HTTPProvider(config.blockchain.monad_rpc_url.replace("wss://", "https://")))
        self._cache = {}

    def is_connected(self) -> bool:
        """Check blockchain connection"""
        return self.w3.is_connected()

    def get_block_number(self) -> int:
        """Get current block number"""
        return self.w3.eth.block_number

    async def get_contract_code(self, address: str, chain_id: int = 10143) -> str:
        """Get the bytecode of a contract."""
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

    async def scan_address(self, address: str, chain_id: int = 10143) -> ScanResult:
        """Perform a complete scan of an address."""
        logger.info(f"Scanning contract: {address}")

        bytecode = await self.get_contract_code(address, chain_id)
        is_contract = bytecode != "0x" and len(bytecode) > 2

        bytecode_hash = ""
        if bytecode:
            bytecode_hash = self.w3.keccak(hexstr=bytecode).hex()

        return ScanResult(
            address=address,
            bytecode=bytecode,
            source_code=None,
            abi=None,
            is_contract=is_contract,
            bytecode_hash=bytecode_hash,
        )

    async def submit_report(self, bounty_id: int, ipfs_hash: str, signature: str) -> str:
        """Submit a vulnerability report to a bounty contract."""
        logger.info(f"Would submit report for bounty {bounty_id}")
        return "0xplaceholder"

    async def create_bounty(self, amount_wei: int, ipfs_hash: str, expires_in: int) -> tuple[int, str]:
        """Create a new bounty."""
        logger.info(f"Creating bounty: {amount_wei} wei")
        return (1, "0xplaceholder")

    async def check_bounty_status(self, bounty_id: int) -> dict:
        """Check the status of a bounty."""
        return {
            "id": bounty_id,
            "claimed": False,
            "disputed": False,
            "expires_at": 0,
        }
