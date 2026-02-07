"""
Cyber-Mercenary Configuration

Loads settings from .env file.
"""

import os
from pathlib import Path

# Load .env file from project root
dotenv_path = Path(__file__).parent.parent.parent / ".env"
if dotenv_path.exists():
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()


class Settings:
    """Simple settings class - reads from environment"""

    # Blockchain
    @property
    def monad_rpc_url(self):
        return os.getenv("MONAD_RPC_URL", "wss://monad-testnet.drpc.org")

    @property
    def monad_chain_id(self):
        return int(os.getenv("MONAD_CHAIN_ID", "10143"))

    @property
    def private_key(self):
        return os.getenv("PRIVATE_KEY")

    @property
    def agent_address(self):
        return os.getenv("AGENT_ADDRESS")

    # MiniMax AI
    @property
    def minimax_api_key(self):
        return os.getenv("MINIMAX_API_KEY", "")

    @property
    def minimax_endpoint(self):
        return os.getenv("MINIMAX_ENDPOINT", "https://api.minimax.chat/v1/text/chatcompletion_v2")

    @property
    def minimax_model(self):
        return os.getenv("MINIMAX_MODEL", "abab6.5s-chat")

    @property
    def minimax_max_tokens(self):
        return int(os.getenv("MINIMAX_MAX_TOKENS", "4096"))

    @property
    def minimax_temperature(self):
        return float(os.getenv("MINIMAX_TEMPERATURE", "0.7"))

    # Database
    @property
    def database_url(self):
        return os.getenv("DATABASE_URL", "sqlite:///./data/cyber_mercenary.db")

    # Agent settings
    @property
    def agent_name(self):
        return os.getenv("AGENT_NAME", "CyberMercenary")

    @property
    def signing_interval_minutes(self):
        return int(os.getenv("SIGNING_INTERVAL_MINUTES", "5"))

    @property
    def scan_interval_minutes(self):
        return int(os.getenv("SCAN_INTERVAL_MINUTES", "30"))

    @property
    def scan_depth(self):
        return os.getenv("SCAN_DEPTH", "standard")

    # Contracts (fill after deployment)
    @property
    def escrow_contract_address(self):
        return os.getenv("ESCROW_CONTRACT_ADDRESS")

    @property
    def bounty_registry_address(self):
        return os.getenv("BOUNTY_REGISTRY_ADDRESS")

    @property
    def signature_verifier_address(self):
        return os.getenv("SIGNATURE_VERIFIER_ADDRESS")

    # IPFS
    @property
    def ipfs_node_url(self):
        return os.getenv("IPFS_NODE_URL", "http://127.0.0.1:5001")

    @property
    def ipfs_gateway(self):
        return os.getenv("IPFS_GATEWAY", "https://gateway.pinata.cloud")

    @property
    def ipfs_api_key(self):
        return os.getenv("IPFS_API_KEY")

    @property
    def ipfs_api_secret(self):
        return os.getenv("IPFS_API_SECRET")

    # Monitoring
    @property
    def log_level(self):
        return os.getenv("LOG_LEVEL", "INFO")

    @property
    def log_file(self):
        return os.getenv("LOG_FILE", "./data/cyber_mercenary.log")

    @property
    def metrics_port(self):
        return int(os.getenv("METRICS_PORT", "9090"))

    @property
    def metrics_enabled(self):
        return os.getenv("METRICS_ENABLED", "true").lower() == "true"

    # Frontend (Viem/Wagmi)
    @property
    def next_public_chain_id(self):
        return int(os.getenv("NEXT_PUBLIC_CHAIN_ID", "10143"))

    @property
    def next_public_escrow_address(self):
        return os.getenv("NEXT_PUBLIC_ESCROW_ADDRESS")

    @property
    def next_public_rpc_url(self):
        return os.getenv("NEXT_PUBLIC_RPC_URL", "wss://monad-testnet.drpc.org")

    def validate(self) -> bool:
        """Validate configuration"""
        if not self.private_key:
            print("ERROR: PRIVATE_KEY not set in .env")
            return False
        if not self.minimax_api_key:
            print("ERROR: MINIMAX_API_KEY not set in .env")
            return False
        return True


# Create singleton instance
settings = Settings()
