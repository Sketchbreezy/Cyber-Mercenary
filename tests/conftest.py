"""
Pytest configuration and fixtures for Cyber-Mercenary tests.
"""

import sys
from pathlib import Path
import pytest
import asyncio

# Add agent/src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "agent" / "src"))


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    class MockBlockchainConfig:
        monad_rpc_url = "https://monad-testnet.drpc.org"
        monad_chain_id = 10143
        private_key = "0x0000000000000000000000000000000000000000000000000000000000000001"
        agent_address = "0x0000000000000000000000000000000000000001"

    class MockMiniMaxConfig:
        api_key = "test-api-key"
        endpoint = "https://openrouter.ai/api/v1/chat/completions"
        model = "minimax/minimax-m2.1"
        max_tokens = 4096
        temperature = 0.7

    class MockContractsConfig:
        escrow = "0x705a3a2be44Ad0b00f291314a6818EDF9d77071a"

    class MockDatabaseConfig:
        url = ":memory:"

    class MockSettings:
        blockchain = MockBlockchainConfig()
        minimax = MockMiniMaxConfig()
        contracts = MockContractsConfig()
        database = MockDatabaseConfig()

    return MockSettings()


@pytest.fixture
def sample_bytecode():
    """Sample contract bytecode for testing."""
    return "0x608060405234801561001057600080fd5b5060bf8061001f6000396000f3fe6080604052348015600f57600080fd5b506004361060325760003560e01c8063368b4772146037578063d826f88f146068575b600080fd5b606660048036038101906062919060ba565b600055565b60005460749060d6565b60405180910390f35b600080fd5b609c8160eb565b811460a657600080fd5b50565b600081359050610ba565b600080fd5b600080fd5b6000601f19601f83011690549093919060d6565b6040519080825280601f01601f19166020018201604052801561010657816000f55b50505056"


@pytest.fixture
def sample_signature():
    """Sample ECDSA signature for testing."""
    return "0x1c8aff9502657a25b7d7704e53d3f8c5a6c7e7d8c8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8"


@pytest.fixture
def sample_scan_data():
    """Sample scan request data."""
    return {
        "contract_address": "0x705a3a2be44Ad0b00f291314a6818EDF9d77071a",
        "chain_id": 10143,
        "scan_depth": "standard"
    }


@pytest.fixture
def sample_bounty_data():
    """Sample bounty request data."""
    return {
        "amount_wei": 1000000000000000,  # 0.001 ETH
        "ipfs_hash": "QmTest123456789",
        "expires_in": 86400  # 24 hours
    }
