"""
Cyber-Mercenary Configuration

Loads settings from environment variables with validation.
"""

import os
from pathlib import Path
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class BlockchainConfig(BaseModel):
    """Blockchain configuration"""
    monad_rpc_url: str = Field(
        default="wss://monad-testnet.drpc.org",
        description="Monad RPC endpoint"
    )
    monad_chain_id: int = Field(default=10143, description="Monad chain ID")
    private_key: Optional[str] = Field(default=None, description="Agent wallet private key")
    agent_address: Optional[str] = Field(default=None, description="Agent wallet address")

    @property
    def is_configured(self) -> bool:
        return bool(self.private_key)


class MiniMaxConfig(BaseModel):
    """MiniMax AI configuration"""
    api_key: str = Field(default="", description="MiniMax API key")
    endpoint: str = Field(
        default="https://api.minimax.chat/v1/text/chatcompletion_v2",
        description="MiniMax API endpoint"
    )
    model: str = Field(default="abab6.5s-chat", description="MiniMax model")
    max_tokens: int = Field(default=4096, description="Max response tokens")
    temperature: float = Field(default=0.7, description="Model temperature")


class DatabaseConfig(BaseModel):
    """Database configuration"""
    url: str = Field(
        default="sqlite:///./data/cyber_mercenary.db",
        description="Database connection URL"
    )
    pool_size: int = Field(default=10, description="Connection pool size")


class AgentConfig(BaseModel):
    """Agent runtime configuration"""
    name: str = Field(default="CyberMercenary", description="Agent name")
    signing_interval_minutes: int = Field(default=5, description="Signing interval")
    scan_interval_minutes: int = Field(default=30, description="Scan interval")
    scan_depth: str = Field(default="standard", description="Scan depth level")


class IPFSConfig(BaseModel):
    """IPFS configuration"""
    node_url: str = Field(default="http://127.0.0.1:5001", description="IPFS node URL")
    gateway: str = Field(
        default="https://gateway.pinata.cloud",
        description="IPFS gateway"
    )
    api_key: Optional[str] = Field(default=None, description="IPFS API key")
    api_secret: Optional[str] = Field(default=None, description="IPFS API secret")


class ContractsConfig(BaseModel):
    """Smart contract addresses"""
    escrow: Optional[str] = Field(default=None, description="Escrow contract address")
    registry: Optional[str] = Field(default=None, description="Registry contract address")


class MonitoringConfig(BaseModel):
    """Monitoring and logging configuration"""
    log_level: str = Field(default="INFO", description="Log level")
    log_file: str = Field(default="./data/agent.log", description="Log file path")
    metrics_port: int = Field(default=9090, description="Metrics port")
    metrics_enabled: bool = Field(default=True, description="Enable metrics")


class Settings(BaseSettings):
    """Main settings class - loads from .env"""

    # Configuration sections
    blockchain: BlockchainConfig = Field(default_factory=BlockchainConfig)
    minimax: MiniMaxConfig = Field(default_factory=MiniMaxConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    ipfs: IPFSConfig = Field(default_factory=IPFSConfig)
    contracts: ContractsConfig = Field(default_factory=ContractsConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"

    def validate(self) -> bool:
        """Validate configuration"""
        if not self.blockchain.is_configured:
            return False

        if not self.minimax.api_key:
            return False

        return True

    def get_web3_config(self) -> dict:
        """Get Web3.py configuration"""
        return {
            "endpoint_uri": self.blockchain.monad_rpc_url,
            "chain_id": self.blockchain.monad_chain_id,
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
