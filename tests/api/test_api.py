"""
Integration tests for the FastAPI endpoints.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add agent/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agent" / "src"))


class TestAPIEndpoints:
    """Integration tests for API endpoints."""

    @pytest.fixture
    def test_client(self, mock_config):
        """Create a test client with mocked services."""
        from api.server import app

        # Patch all service imports
        with patch('api.server.MiniMaxClient') as MockMiniMax, \
             patch('api.server.ContractScanner') as MockScanner, \
             patch('api.server.SignatureManager') as MockSigner, \
             patch('api.server.DatabaseService') as MockDatabase, \
             patch('api.server.settings', mock_config):

            # Configure mocks
            mock_minimax = Mock()
            mock_minimax.analyze_contract = AsyncMock()
            MockMiniMax.return_value = mock_minimax

            mock_scanner = Mock()
            mock_scanner.scan_address = AsyncMock()
            mock_scanner.is_connected.return_value = True
            MockScanner.return_value = mock_scanner

            mock_signer = Mock()
            mock_signer.address = "0x0000000000000000000000000000000000000001"
            mock_signer.sign_warning = Mock()
            MockSigner.return_value = mock_signer

            mock_db = Mock()
            mock_db.save_scan = Mock()
            mock_db.get_scan = Mock(return_value={
                "scan_id": "test_scan",
                "status": "completed",
                "contract_address": "0x123",
                "risk_score": 0.5,
                "vulnerabilities": [],
                "created_at": "2026-02-07T12:00:00"
            })
            mock_db.get_all_scans = Mock(return_value=[])
            mock_db.get_stats = Mock(return_value={
                "contracts_scanned": 10,
                "vulnerabilities_found": 5,
                "bounties_earned": 2,
                "gigs_completed": 0
            })
            MockDatabase.return_value = mock_db

            # Create client with mocked services
            client = TestClient(app)
            yield client, mock_db, mock_scanner, mock_minimax, mock_signer

    def test_health_endpoint(self, test_client):
        """Test the /health endpoint."""
        client, _, _, _, _ = test_client
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "CyberMercenary"

    def test_root_endpoint(self, test_client):
        """Test the root / endpoint."""
        client, _, _, _, _ = test_client
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Cyber-Mercenary"
        assert data["status"] == "running"

    def test_get_nonexistent_scan_returns_404(self, test_client):
        """Test that getting a non-existent scan returns 404."""
        client, mock_db, _, _, _ = test_client
        mock_db.get_scan.return_value = None

        response = client.get("/api/v1/scan/nonexistent")

        assert response.status_code == 404

    def test_get_existing_scan(self, test_client):
        """Test getting an existing scan."""
        client, mock_db, _, _, _ = test_client

        response = client.get("/api/v1/scan/test_scan")

        assert response.status_code == 200
        data = response.json()
        assert data["scan_id"] == "test_scan"
        assert data["status"] == "completed"

    def test_list_scans(self, test_client):
        """Test the /api/v1/scans endpoint."""
        client, mock_db, _, _, _ = test_client
        mock_db.get_all_scans.return_value = [
            {"scan_id": "scan_1", "status": "completed"},
            {"scan_id": "scan_2", "status": "pending"}
        ]

        response = client.get("/api/v1/scans")

        assert response.status_code == 200
        data = response.json()
        assert "scans" in data
        assert len(data["scans"]) == 2

    def test_get_stats(self, test_client):
        """Test the /api/v1/stats endpoint."""
        client, mock_db, _, _, _ = test_client

        response = client.get("/api/v1/stats")

        assert response.status_code == 200
        data = response.json()
        assert "contracts_scanned" in data
        assert "vulnerabilities_found" in data
        assert data["contracts_scanned"] == 10

    def test_get_agent_address(self, test_client):
        """Test the /api/v1/agent/address endpoint."""
        client, _, _, _, mock_signer = test_client

        response = client.get("/api/v1/agent/address")

        assert response.status_code == 200
        data = response.json()
        assert "address" in data
        assert data["address"] == "0x0000000000000000000000000000000000000001"


class TestBountyEndpoints:
    """Tests for bounty-related endpoints."""

    @pytest.fixture
    def bounty_client(self, mock_config):
        """Create a test client for bounty tests."""
        from api.server import app

        with patch('api.server.settings', mock_config):
            client = TestClient(app)
            yield client

    def test_create_bounty_requires_connected_scanner(self, bounty_client, mock_config):
        """Test that bounty creation requires blockchain connection."""
        from api.server import app

        with patch('api.server.scanner') as mock_scanner, \
             patch('api.server.settings', mock_config):
            mock_scanner.is_connected.return_value = False

            response = bounty_client.post(
                "/api/v1/bounty/create",
                json={
                    "amount_wei": 1000000000000000,
                    "ipfs_hash": "QmTest123",
                    "expires_in": 86400
                }
            )

            assert response.status_code == 503
            assert "not connected" in response.json()["detail"].lower()

    def test_dispute_bounty_requires_connection(self, bounty_client):
        """Test that dispute requires blockchain connection."""
        response = bounty_client.post(
            "/api/v1/bounty/1/dispute",
            json={"bounty_id": 1}
        )

        # Should fail because scanner is not connected in mock
        assert response.status_code in [400, 503]


class TestSignatureEndpoints:
    """Tests for signature-related endpoints."""

    @pytest.fixture
    def signer_client(self, mock_config):
        """Create a test client for signature tests."""
        from api.server import app

        with patch('api.server.settings', mock_config):
            client = TestClient(app)
            yield client

    def test_sign_message(self, signer_client, mock_config):
        """Test the /api/v1/sign endpoint."""
        from api.server import app

        with patch('api.server.signer') as mock_signer, \
             patch('api.server.settings', mock_config):
            mock_signer.sign_message.return_value = Mock(
                message="Test message",
                signature="0x123...",
                hash="0x456...",
                signer_address="0x789..."
            )

            response = signer_client.post(
                "/api/v1/sign",
                json={"message": "Test message"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Test message"
            assert "signature" in data
            assert "hash" in data

    def test_verify_valid_signature(self, signer_client, mock_config):
        """Test signature verification with valid signature."""
        from api.server import app

        with patch('api.server.signer') as mock_signer, \
             patch('api.server.settings', mock_config):
            mock_signer.verify_signature.return_value = True

            response = signer_client.post(
                "/api/v1/verify",
                json={
                    "message": "Test message",
                    "signature": "0xvalid...",
                    "address": "0x123..."
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True

    def test_verify_invalid_signature(self, signer_client, mock_config):
        """Test signature verification with invalid signature."""
        from api.server import app

        with patch('api.server.signer') as mock_signer, \
             patch('api.server.settings', mock_config):
            mock_signer.verify_signature.return_value = False

            response = signer_client.post(
                "/api/v1/verify",
                json={
                    "message": "Test message",
                    "signature": "0xinvalid...",
                    "address": "0x123..."
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False
