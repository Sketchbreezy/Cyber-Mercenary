"""
Contract Scanner Service

Handles blockchain interaction for contract scanning and bounty operations.
"""

import logging
from typing import Optional, Tuple
from dataclasses import dataclass

from web3 import Web3

logger = logging.getLogger(__name__)


# Escrow Contract ABI
ESCROW_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint256", "name": "id", "type": "uint256"},
            {"indexed": True, "internalType": "address", "name": "developer", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"},
            {"indexed": False, "internalType": "string", "name": "ipfsHash", "type": "string"}
        ],
        "name": "BountyCreated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint256", "name": "id", "type": "uint256"},
            {"indexed": True, "internalType": "address", "name": "claimer", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "BountyClaimed",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "uint256", "name": "id", "type": "uint256"}],
        "name": "BountyDisputed",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [{"indexed": True, "internalType": "uint256", "name": "id", "type": "uint256"}],
        "name": "BountyResolved",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [{"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}],
        "name": "FeeCollected",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "MIN_BOUNTY",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "bountyCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "bounties",
        "outputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "address payable", "name": "developer", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "bool", "name": "claimed", "type": "bool"},
            {"internalType": "bool", "name": "disputed", "type": "bool"},
            {"internalType": "string", "name": "ipfsHash", "type": "string"},
            {"internalType": "bytes", "name": "agentSignature", "type": "bytes"},
            {"internalType": "uint256", "name": "createdAt", "type": "uint256"},
            {"internalType": "uint256", "name": "expiresAt", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "ipfsHash", "type": "string"}, {"internalType": "uint256", "name": "expiresIn", "type": "uint256"}],
        "name": "createBounty",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "bountyId", "type": "uint256"}],
        "name": "claimBounty",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "collectFees",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "bountyId", "type": "uint256"}],
        "name": "disputeBounty",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "bountyId", "type": "uint256"}, {"internalType": "bool", "name": "rewardDeveloper", "type": "bool"}],
        "name": "resolveDispute",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "bountyId", "type": "uint256"}, {"internalType": "bytes", "name": "signature", "type": "bytes"}],
        "name": "submitReport",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]


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
        self._escrow_contract = None

    def _get_escrow_contract(self):
        """Get or create the Escrow contract instance"""
        if self._escrow_contract is None and self.config.contracts.escrow:
            self._escrow_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.config.contracts.escrow),
                abi=ESCROW_ABI
            )
        return self._escrow_contract

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

    def _sign_and_send(self, tx) -> str:
        """Sign and send a transaction, return tx hash"""
        signed = self.w3.eth.account.sign_transaction(tx, self.config.blockchain.private_key)
        # Handle both old and new web3.py versions
        raw_tx = getattr(signed, 'rawTransaction', None) or getattr(signed, 'raw_transaction', None)
        tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
        return tx_hash.hex()

    async def create_bounty(self, amount_wei: int, ipfs_hash: str, expires_in: int = 86400) -> Tuple[int, str]:
        """
        Create a new bounty on-chain.
        
        Args:
            amount_wei: Bounty amount in wei
            ipfs_hash: IPFS hash of the report template
            expires_in: Time until expiry (seconds)
            
        Returns:
            Tuple of (bounty_id, transaction_hash)
        """
        escrow = self._get_escrow_contract()
        if not escrow:
            logger.warning("Escrow contract not configured, using placeholder")
            return (1, "0xplaceholder")

        try:
            # Build transaction
            tx = escrow.functions.createBounty(ipfs_hash, expires_in).build_transaction({
                'from': self.config.blockchain.agent_address or self.w3.eth.accounts[0] if not self.config.blockchain.private_key else Web3().eth.account.from_key(self.config.blockchain.private_key).address,
                'value': amount_wei,
                'gas': 300000,
                'nonce': self.w3.eth.get_transaction_count(
                    Web3().eth.account.from_key(self.config.blockchain.private_key).address
                ),
                'chainId': self.config.blockchain.monad_chain_id
            })

            # Sign and send
            tx_hash = self._sign_and_send(tx)
            
            # Get bounty ID from event (simplified - returns current count)
            bounty_id = escrow.functions.bountyCount().call()
            
            logger.info(f"✅ Bounty created: ID={bounty_id}, Tx={tx_hash[:16]}...")
            return (bounty_id, tx_hash)

        except Exception as e:
            logger.error(f"Failed to create bounty: {e}")
            return (0, f"error: {str(e)}")

    async def claim_bounty(self, bounty_id: int) -> str:
        """
        Claim a bounty.
        
        Args:
            bounty_id: The bounty ID to claim
            
        Returns:
            Transaction hash
        """
        escrow = self._get_escrow_contract()
        if not escrow:
            return "0xplaceholder"

        try:
            tx = escrow.functions.claimBounty(bounty_id).build_transaction({
                'from': Web3().eth.account.from_key(self.config.blockchain.private_key).address,
                'gas': 300000,
                'nonce': self.w3.eth.get_transaction_count(
                    Web3().eth.account.from_key(self.config.blockchain.private_key).address
                ),
                'chainId': self.config.blockchain.monad_chain_id
            })

            tx_hash = self._sign_and_send(tx)
            logger.info(f"✅ Bounty {bounty_id} claimed: Tx={tx_hash[:16]}...")
            return tx_hash

        except Exception as e:
            logger.error(f"Failed to claim bounty: {e}")
            return f"error: {str(e)}"

    async def dispute_bounty(self, bounty_id: int) -> str:
        """
        File a dispute for a bounty.
        
        Args:
            bounty_id: The bounty ID to dispute
            
        Returns:
            Transaction hash
        """
        escrow = self._get_escrow_contract()
        if not escrow:
            return "0xplaceholder"

        try:
            tx = escrow.functions.disputeBounty(bounty_id).build_transaction({
                'from': Web3().eth.account.from_key(self.config.blockchain.private_key).address,
                'gas': 300000,
                'nonce': self.w3.eth.get_transaction_count(
                    Web3().eth.account.from_key(self.config.blockchain.private_key).address
                ),
                'chainId': self.config.blockchain.monad_chain_id
            })

            tx_hash = self._sign_and_send(tx)
            logger.info(f"✅ Bounty {bounty_id} disputed: Tx={tx_hash[:16]}...")
            return tx_hash

        except Exception as e:
            logger.error(f"Failed to dispute bounty: {e}")
            return f"error: {str(e)}"

    async def resolve_dispute(self, bounty_id: int, reward_developer: bool) -> str:
        """
        Resolve a dispute.
        
        Args:
            bounty_id: The bounty ID to resolve
            reward_developer: True to reward developer, False to refund
            
        Returns:
            Transaction hash
        """
        escrow = self._get_escrow_contract()
        if not escrow:
            return "0xplaceholder"

        try:
            tx = escrow.functions.resolveDispute(bounty_id, reward_developer).build_transaction({
                'from': Web3().eth.account.from_key(self.config.blockchain.private_key).address,
                'gas': 300000,
                'nonce': self.w3.eth.get_transaction_count(
                    Web3().eth.account.from_key(self.config.blockchain.private_key).address
                ),
                'chainId': self.config.blockchain.monad_chain_id
            })

            tx_hash = self._sign_and_send(tx)
            logger.info(f"✅ Bounty {bounty_id} resolved (reward={reward_developer}): Tx={tx_hash[:16]}...")
            return tx_hash

        except Exception as e:
            logger.error(f"Failed to resolve dispute: {e}")
            return f"error: {str(e)}"

    async def submit_report(self, bounty_id: int, signature: str) -> str:
        """
        Submit a vulnerability report with signature.
        
        Args:
            bounty_id: The bounty ID
            signature: ECDSA signature
            
        Returns:
            Transaction hash
        """
        escrow = self._get_escrow_contract()
        if not escrow:
            return "0xplaceholder"

        try:
            tx = escrow.functions.submitReport(bounty_id, signature).build_transaction({
                'from': Web3().eth.account.from_key(self.config.blockchain.private_key).address,
                'gas': 300000,
                'nonce': self.w3.eth.get_transaction_count(
                    Web3().eth.account.from_key(self.config.blockchain.private_key).address
                ),
                'chainId': self.config.blockchain.monad_chain_id
            })

            tx_hash = self._sign_and_send(tx)
            logger.info(f"✅ Report submitted for bounty {bounty_id}: Tx={tx_hash[:16]}...")
            return tx_hash

        except Exception as e:
            logger.error(f"Failed to submit report: {e}")
            return f"error: {str(e)}"

    async def get_bounty_status(self, bounty_id: int) -> dict:
        """
        Get the status of a bounty.
        
        Args:
            bounty_id: The bounty ID
            
        Returns:
            Bounty status dictionary
        """
        escrow = self._get_escrow_contract()
        if not escrow:
            return {
                "id": bounty_id,
                "claimed": False,
                "disputed": False,
                "expires_at": 0,
                "status": "unknown"
            }

        try:
            bounty = escrow.functions.bounties(bounty_id).call()
            return {
                "id": bounty_id,
                "developer": bounty[1],
                "amount": bounty[2],
                "claimed": bounty[3],
                "disputed": bounty[4],
                "ipfsHash": bounty[5],
                "expiresAt": bounty[8],
                "status": "disputed" if bounty[4] else ("claimed" if bounty[3] else "active")
            }
        except Exception as e:
            logger.error(f"Failed to get bounty status: {e}")
            return {"error": str(e)}
