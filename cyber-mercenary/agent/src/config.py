"""
Cyber-Mercenary Configuration

Loads settings from .env file with nested structure for services.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class BlockchainConfig:
    """Blockchain configuration"""
    monad_rpc_url: str = "wss://monad-testnet.drpc.org"
    monad_chain_id: int = 10143
    private_key: Optional[str] = None
    agent_address: Optional[str] = None


@dataclass
class MiniMaxConfig:
    """MiniMax AI configuration"""
    api_key: str = ""
    endpoint: str = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    model: str = "abab6.5s-chat"
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class ContractsConfig:
    """Contract addresses"""
    escrow: Optional[str] = None
    bounty_registry: Optional[str] = None
    signature_verifier: Optional[str] = None


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite:///./data/cyber_mercenary.db"


@dataclass
class AgentConfig:
    """Agent settings"""
    name: str = "CyberMercenary"
    scan_interval_minutes: int = 30
    signing_interval_minutes: int = 5
    scan_depth: str = "standard"


class Settings:
    """Main settings class"""

    def __init__(self):
        # Load .env file
        dotenv_path = Path(__file__).parent.parent.parent / ".env"
        if dotenv_path.exists():
            with open(dotenv_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()

        # Initialize subconfigs
        self.blockchain = BlockchainConfig(
            monad_rpc_url=os.getenv("MONAD_RPC_URL", "wss://monad-testnet.drpc.org"),
            monad_chain_id=int(os.getenv("MONAD_CHAIN_ID", "10143")),
            private_key=os.getenv("PRIVATE_KEY"),
            agent_address=os.getenv("AGENT_ADDRESS"),
        )

        self.minimax = MiniMaxConfig(
            api_key=os.getenv("MINIMAX_API_KEY", ""),
            endpoint=os.getenv("MINIMAX_ENDPOINT", "https://openrouter.ai/api/v1/chat/completions"),
            model=os.getenv("MINIMAX_MODEL", "minimax/minimax-m2"),
            max_tokens=int(os.getenv("MINIMAX_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("MINIMAX_TEMPERATURE", "0.7")),
        )

        self.contracts = ContractsConfig(
            escrow=os.getenv("ESCROW_CONTRACT_ADDRESS"),
            bounty_registry=os.getenv("BOUNTY_REGISTRY_ADDRESS"),
            signature_verifier=os.getenv("SIGNATURE_VERIFIER_ADDRESS"),
        )

        self.database = DatabaseConfig(
            url=os.getenv("DATABASE_URL", "sqlite:///./data/cyber_mercenary.db"),
        )

        self.agent = AgentConfig(
            name=os.getenv("AGENT_NAME", "CyberMercenary"),
            scan_interval_minutes=int(os.getenv("SCAN_INTERVAL_MINUTES", "30")),
            signing_interval_minutes=int(os.getenv("SIGNING_INTERVAL_MINUTES", "5")),
            scan_depth=os.getenv("SCAN_DEPTH", "standard"),
        )

    def validate(self) -> bool:
        """Validate required configuration"""
        if not self.blockchain.private_key:
            print("ERROR: PRIVATE_KEY not set in .env")
            return False
        return True


# Create singleton instance
settings = Settings()
