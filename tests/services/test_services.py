"""
Service tests for the Cyber-Mercenary services.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock


class TestSignatureManager:
    """Tests for the SignatureManager service."""

    def test_initialization_without_key(self):
        """Test initialization fails without private key."""
        from services.signer import SignatureManager

        mock_config = Mock()
        mock_config.blockchain.private_key = None

        manager = SignatureManager(mock_config)

        with pytest.raises(ValueError, match="Private key not configured"):
            manager._get_account()

    def test_sign_message_structure(self, mock_config):
        """Test sign_message returns correct structure."""
        from services.signer import SignatureManager

        manager = SignatureManager(mock_config)
        result = manager.sign_message("Test message")

        assert result.message == "Test message"
        assert result.signature.startswith("0x")
        assert result.hash.startswith("0x")
        assert result.signer_address.startswith("0x")

    def test_verify_signature_valid(self, mock_config):
        """Test signature verification with valid signature."""
        from services.signer import SignatureManager

        manager = SignatureManager(mock_config)
        signed = manager.sign_message("Test message")

        is_valid = manager.verify_signature(
            "Test message",
            signed.signature,
            signed.signer_address
        )

        assert is_valid is True

    def test_verify_signature_invalid(self, mock_config):
        """Test signature verification with invalid signature."""
        from services.signer import SignatureManager

        manager = SignatureManager(mock_config)

        is_valid = manager.verify_signature(
            "Test message",
            "0x" + "00" * 65,
            manager.address
        )

        assert is_valid is False


class TestMiniMaxClient:
    """Tests for the MiniMax client service."""

    @pytest.mark.asyncio
    async def test_analyze_contract_structure(self, mock_config):
        """Test analyze_contract returns correct structure."""
        from services.minimax import MiniMaxClient, ContractAnalysis

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '{"vulnerabilities": [], "overall_risk_score": 0.0, "summary": "No issues"}'
                    }
                }]
            }

            client = MiniMaxClient(mock_config)
            result = await client.analyze_contract("0x60606040")

            assert isinstance(result, ContractAnalysis)
            assert isinstance(result.vulnerabilities, list)
            assert isinstance(result.overall_risk_score, float)
            assert isinstance(result.summary, str)

    @pytest.mark.asyncio
    async def test_analyze_contract_handles_empty_response(self, mock_config):
        """Test handling of empty AI response."""
        from services.minimax import MiniMaxClient

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = {
                "choices": [{
                    "message": {
                        "content": ""
                    }
                }]
            }

            client = MiniMaxClient(mock_config)
            result = await client.analyze_contract("0x60606040")

            assert result.overall_risk_score == 0
            assert len(result.vulnerabilities) == 0


class TestDatabaseService:
    """Tests for the database service."""

    def test_save_scan_record(self, db_service):
        """Test saving a scan record."""
        from services.database import DatabaseService

        scan_id = db_service.save_scan(
            scan_id="test_scan_001",
            contract_address="0x1234567890123456789012345678901234567890",
            chain_id=10143,
            status="completed",
            risk_score=0.75,
            vulnerability_count=3
        )

        assert scan_id is not None

    def test_get_scan_by_id(self, db_service):
        """Test retrieving a scan by ID."""
        from services.database import DatabaseService

        # Save
        db_service.save_scan(
            scan_id="test_scan_002",
            contract_address="0xabcd567890123456789012345678901234567890",
            status="completed"
        )

        # Retrieve
        scan = db_service.get_scan("test_scan_002")

        assert scan is not None
        assert scan["scan_id"] == "test_scan_002"
        assert scan["contract_address"] == "0xabcd567890123456789012345678901234567890"

    def test_save_and_get_bounty(self, db_service):
        """Test saving and retrieving a bounty."""
        from services.database import DatabaseService

        bounty_id = db_service.save_bounty(
            bounty_id=1,
            contract_address="0x1234567890123456789012345678901234567890",
            amount_wei=1000000000000000,
            status="active"
        )

        assert bounty_id is not None

        bounty = db_service.get_bounty(1)
        assert bounty is not None
        assert bounty["bounty_id"] == 1
        assert bounty["amount_wei"] == 1000000000000000

    def test_claim_bounty(self, db_service):
        """Test claiming a bounty."""
        from services.database import DatabaseService

        db_service.save_bounty(
            bounty_id=2,
            status="active"
        )

        result = db_service.claim_bounty(2)
        assert result is True

        bounty = db_service.get_bounty(2)
        assert bounty["claimed_at"] is not None

    def test_get_statistics(self, db_service):
        """Test retrieving statistics."""
        from services.database import DatabaseService

        # Add some data
        for i in range(3):
            db_service.save_scan(
                scan_id=f"stat_test_{i}",
                contract_address=f"0x{i:040d}",
                vulnerability_count=i + 1
            )

        stats = db_service.get_stats()

        assert "contracts_scanned" in stats
        assert "vulnerabilities_found" in stats
        assert stats["contracts_scanned"] >= 3
