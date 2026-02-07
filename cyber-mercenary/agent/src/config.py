"""
Cyber-Mercenary Configuration

Loads settings from environment variables.
"""

import os
from pathlib import Path


class Settings:
    """Simple settings class - no pydantic validation"""

    # Blockchain
    monad_rpc_url = os.getenv("MONAD_RPC_URL", "wss://monad-testnet.drpc.org")
    monad_chain_id = int(os.getenv("MONAD_CHAIN_ID", "10143"))
    private_key = os.getenv("PRIVATE_KEY")
    agent_address = os.getenv("AGENT_ADDRESS")

    # MiniMax AI
    minimax_api_key = os.getenv("MINIMAX_API_KEY", "")
    minimax_endpoint = os.getenv("MINIMAX_ENDPOINT", "https://api.minimax.chat/v1/text/chatcompletion_v2")
    minimax_model = os.getenv("MINIMAX_MODEL", "abab6.5s-chat")
    minimax_max_tokens = int(os.getenv("MINIMAX_MAX_TOKENS", "4096"))
    minimax_temperature = float(os.getenv("MINIMAX_TEMPERATURE", "0.7"))

    # Database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./data/cyber_mercenary.db")

    # Agent settings
    agent_name = os.getenv("AGENT_NAME", "CyberMercenary")
    signing_interval_minutes = int(os.getenv("SIGNING_INTERVAL_MINUTES", "5"))
    scan_interval_minutes = int(os.getenv("SCAN_INTERVAL_MINUTES", "30"))
    scan_depth = os.getenv("SCAN_DEPTH", "standard")

    # Contracts (fill after deployment)
    escrow_contract_address = os.getenv("ESCROW_CONTRACT_ADDRESS")
    bounty_registry_address = os.getenv("BOUNTY_REGISTRY_ADDRESS")
    signature_verifier_address = os.getenv("SIGNATURE_VERIFIER_ADDRESS")

    # IPFS
    ipfs_node_url = os.getenv("IPFS_NODE_URL", "http://127.0.0.1:5001")
    ipfs_gateway = os.getenv("IPFS_GATEWAY", "https://gateway.pinata.cloud")
    ipfs_api_key = os.getenv("IPFS_API_KEY")
    ipfs_api_secret = os.getenv("IPFS_API_SECRET")

    # Monitoring
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "./data/cyber_mercenary.log")
    metrics_port = int(os.getenv("METRICS_PORT", "9090"))
    metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"

    # Frontend (Viem/Wagmi)
    next_public_chain_id = int(os.getenv("NEXT_PUBLIC_CHAIN_ID", "10143"))
    next_public_escrow_address = os.getenv("NEXT_PUBLIC_ESCROW_ADDRESS")
    next_public_rpc_url = os.getenv("NEXT_PUBLIC_RPC_URL", "wss://monad-testnet.drpc.org")

    def validate(self) -> bool:
        """Validate configuration"""
        if not self.private_key:
            return False
        if not self.minimax_api_key:
            return False
        return True
