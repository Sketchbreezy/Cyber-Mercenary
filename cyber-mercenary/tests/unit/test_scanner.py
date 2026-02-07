"""
Unit tests for the Contract Scanner Service.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock


class TestContractScanner:
    """Tests for the ContractScanner class."""

    @pytest.fixture
    def mock_web3(self):
        """Mock Web3 responses."""
        with patch('web3.Web3') as MockWeb3:
            mock_instance = Mock()
            mock_instance.is_connected.return_value = True
            mock_instance.eth.block_number = 1000
            mock_instance.eth.get_code.return_value = b'\x60\x80\x60\x04\x3b'
            mock_instance.eth.get_transaction_count.return_value = 5
            mock_instance.eth.send_raw_transaction.return_value = Mock(hex=lambda: "0xabc123")
            mock_instance.keccak.return_value = bytes(32)
            MockWeb3.return_value = mock_instance
            yield mock_instance

    def test_scanner_initialization(self, mock_config):
        """Test that scanner initializes correctly."""
        from services.scanner import ContractScanner

        scanner = ContractScanner(mock_config)

        assert scanner.w3 is not None
        assert scanner._cache == {}

    def test_is_connected(self, mock_config):
        """Test blockchain connection check."""
        from services.scanner import ContractScanner

        scanner = ContractScanner(mock_config)

        with patch.object(scanner.w3, 'is_connected', return_value=True):
            assert scanner.is_connected() is True

        with patch.object(scanner.w3, 'is_connected', return_value=False):
            assert scanner.is_connected() is False

    def test_get_block_number(self, mock_config):
        """Test getting current block number."""
        from services.scanner import ContractScanner

        scanner = ContractScanner(mock_config)

        with patch.object(scanner.w3.eth, 'block_number', 5000):
            assert scanner.get_block_number() == 5000

    @pytest.mark.asyncio
    async def test_get_contract_code(self, mock_config):
        """Test getting contract bytecode."""
        from services.scanner import ContractScanner

        scanner = ContractScanner(mock_config)

        with patch.object(scanner.w3.eth, 'get_code', return_value=b'\x60\x80'):
            code = await scanner.get_contract_code("0x1234567890123456789012345678901234567890")

            assert code == "6080"
            assert "0x1234" in scanner._cache

    @pytest.mark.asyncio
    async def test_get_contract_code_caching(self, mock_config):
        """Test that contract code is cached."""
        from services.scanner import ContractScanner

        scanner = ContractScanner(mock_config)

        with patch.object(scanner.w3.eth, 'get_code', return_value=b'\x60\x80') as mock_get:
            # First call
            await scanner.get_contract_code("0x1234")

            # Second call should use cache
            await scanner.get_contract_code("0x1234")

            # Should only be called once
            assert mock_get.call_count == 1

    @pytest.mark.asyncio
    async def test_scan_address_is_contract(self, mock_config):
        """Test scanning an address that is a contract."""
        from services.scanner import ContractScanner, ScanResult

        scanner = ContractScanner(mock_config)

        bytecode = "0x6080604052348015600f57600080fd5b506004361060325760003560e01c8063368b4772146037578063d826f88f146068575b600080fd5b606660048036038101906062919060ba565b600055565b60005460749060d6565b60405180910390f35b600080fd5b609c8160eb565b811460a657600080fd5b50565b600081359050610ba565b600080fd5b600080fd5b6000601f19601f83011690549093919060d6565b6040519080825280601f01601f19166020018201604052801561010657816000f55b50505056"

        with patch.object(scanner.w3.eth, 'get_code', return_value=bytecode):
            result = await scanner.scan_address("0x1234567890123456789012345678901234567890")

            assert isinstance(result, ScanResult)
            assert result.is_contract is True
            assert result.bytecode == bytecode

    @pytest.mark.asyncio
    async def test_scan_address_not_contract(self, mock_config):
        """Test scanning an address that is not a contract."""
        from services.scanner import ContractScanner, ScanResult

        scanner = ContractScanner(mock_config)

        with patch.object(scanner.w3.eth, 'get_code', return_value=b'\x00'):
            result = await scanner.scan_address("0x1234567890123456789012345678901234567890")

            assert isinstance(result, ScanResult)
            assert result.is_contract is False

    @pytest.mark.asyncio
    async def test_scan_address_handles_error(self, mock_config):
        """Test scanning handles errors gracefully."""
        from services.scanner import ContractScanner, ScanResult

        scanner = ContractScanner(mock_config)

        with patch.object(scanner.w3.eth, 'get_code', side_effect=Exception("RPC error")):
            result = await scanner.scan_address("0x1234567890123456789012345678901234567890")

            assert isinstance(result, ScanResult)
            assert result.is_contract is False
            assert result.bytecode == ""

    def test_get_escrow_contract(self, mock_config):
        """Test getting escrow contract instance."""
        from services.scanner import ContractScanner

        scanner = ContractScanner(mock_config)

        contract = scanner._get_escrow_contract()

        assert contract is not None
        assert contract.address == mock_config.contracts.escrow

    @pytest.mark.asyncio
    async def test_get_bounty_status_unknown(self, mock_config):
        """Test getting bounty status when contract not available."""
        from services.scanner import ContractScanner

        mock_config_no_contract = Mock()
        mock_config_no_contract.contracts.escrow = None

        scanner = ContractScanner(mock_config_no_contract)

        status = await scanner.get_bounty_status(1)

        assert status["status"] == "unknown"
        assert status["id"] == 1

    @pytest.mark.asyncio
    async def test_create_bounty_without_contract(self, mock_config):
        """Test creating bounty when escrow contract not configured."""
        from services.scanner import ContractScanner

        mock_config_no_contract = Mock()
        mock_config_no_contract.contracts.escrow = None
        mock_config_no_contract.blockchain.agent_address = "0x1234"

        scanner = ContractScanner(mock_config_no_contract)

        bounty_id, tx_hash = await scanner.create_bounty(1000000, "QmTest", 86400)

        assert bounty_id == 1
        assert tx_hash == "0xplaceholder"

    @pytest.mark.asyncio
    async def test_claim_bounty_without_contract(self, mock_config):
        """Test claiming bounty when escrow contract not configured."""
        from services.scanner import ContractScanner

        mock_config_no_contract = Mock()
        mock_config_no_contract.contracts.escrow = None

        scanner = ContractScanner(mock_config_no_contract)

        tx_hash = await scanner.claim_bounty(1)

        assert tx_hash == "0xplaceholder"

    @pytest.mark.asyncio
    async def test_dispute_bounty_without_contract(self, mock_config):
        """Test disputing bounty when escrow contract not configured."""
        from services.scanner import ContractScanner

        mock_config_no_contract = Mock()
        mock_config_no_contract.contracts.escrow = None

        scanner = ContractScanner(mock_config_no_contract)

        tx_hash = await scanner.dispute_bounty(1)

        assert tx_hash == "0xplaceholder"

    @pytest.mark.asyncio
    async def test_resolve_dispute_without_contract(self, mock_config):
        """Test resolving dispute when escrow contract not configured."""
        from services.scanner import ContractScanner

        mock_config_no_contract = Mock()
        mock_config_no_contract.contracts.escrow = None

        scanner = ContractScanner(mock_config_no_contract)

        tx_hash = await scanner.resolve_dispute(1, True)

        assert tx_hash == "0xplaceholder"
