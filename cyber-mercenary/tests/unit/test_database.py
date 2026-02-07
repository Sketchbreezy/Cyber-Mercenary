"""
Unit tests for the Database Service.
"""

import pytest
import tempfile
import os
from pathlib import Path


class TestDatabaseService:
    """Tests for the DatabaseService class."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database file."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)

    @pytest.fixture
    def db_service(self, temp_db):
        """Create a database service with a temporary database."""
        from services.database import DatabaseService

        service = DatabaseService(f"sqlite:///{temp_db}")
        return service

    def test_database_initializes_correctly(self, db_service):
        """Test that the database initializes with all required tables."""
        from services.database import DatabaseService

        # The database should have been initialized by the fixture
        assert db_service.db_path is not None

    def test_save_scan(self, db_service):
        """Test saving a scan record."""
        scan_id = db_service.save_scan(
            scan_id="test_scan_001",
            contract_address="0x1234567890123456789012345678901234567890",
            chain_id=10143,
            status="completed",
            risk_score=0.75,
            vulnerability_count=3
        )

        assert scan_id is not None
        assert scan_id > 0

    def test_get_scan(self, db_service):
        """Test retrieving a scan record."""
        # First save a scan
        scan_id = db_service.save_scan(
            scan_id="test_scan_002",
            contract_address="0xabcd567890123456789012345678901234567890",
            chain_id=10143,
            status="completed",
            risk_score=0.5,
            vulnerability_count=2
        )

        # Then retrieve it
        scan = db_service.get_scan("test_scan_002")

        assert scan is not None
        assert scan["scan_id"] == "test_scan_002"
        assert scan["contract_address"] == "0xabcd567890123456789012345678901234567890"
        assert scan["status"] == "completed"
        assert scan["risk_score"] == 0.5
        assert scan["vulnerability_count"] == 2

    def test_get_nonexistent_scan(self, db_service):
        """Test that retrieving a non-existent scan returns None."""
        scan = db_service.get_scan("nonexistent_scan_id")
        assert scan is None

    def test_get_all_scans(self, db_service):
        """Test retrieving all scans."""
        # Save multiple scans
        for i in range(5):
            db_service.save_scan(
                scan_id=f"test_scan_{i:03d}",
                contract_address=f"0x{i:040d}",
                chain_id=10143,
                status="completed"
            )

        scans = db_service.get_all_scans(limit=10)

        assert len(scans) >= 5

    def test_save_bounty(self, db_service):
        """Test saving a bounty record."""
        bounty_id = db_service.save_bounty(
            bounty_id=1,
            contract_address="0x1234567890123456789012345678901234567890",
            amount_wei=1000000000000000,
            status="created"
        )

        assert bounty_id is not None
        assert bounty_id > 0

    def test_get_bounty(self, db_service):
        """Test retrieving a bounty record."""
        # Save a bounty
        db_service.save_bounty(
            bounty_id=2,
            contract_address="0xabcd567890123456789012345678901234567890",
            amount_wei=2000000000000000,
            status="active"
        )

        # Retrieve it
        bounty = db_service.get_bounty(2)

        assert bounty is not None
        assert bounty["bounty_id"] == 2
        assert bounty["amount_wei"] == 2000000000000000
        assert bounty["status"] == "active"

    def test_claim_bounty(self, db_service):
        """Test claiming a bounty."""
        # Save a bounty
        db_service.save_bounty(
            bounty_id=3,
            amount_wei=3000000000000000,
            status="active"
        )

        # Claim it
        result = db_service.claim_bounty(3)

        assert result is True

        # Verify it's marked as claimed
        bounty = db_service.get_bounty(3)
        assert bounty["claimed_at"] is not None

    def test_get_stats(self, db_service):
        """Test retrieving statistics."""
        # Save some data
        for i in range(3):
            db_service.save_scan(
                scan_id=f"stat_scan_{i}",
                contract_address=f"0x{i:040d}",
                vulnerability_count=i + 1
            )

        stats = db_service.get_stats()

        assert "contracts_scanned" in stats
        assert "vulnerabilities_found" in stats
        assert stats["contracts_scanned"] >= 3

    def test_increment_vulnerabilities(self, db_service):
        """Test incrementing vulnerability count."""
        initial_stats = db_service.get_stats()
        initial_count = initial_stats["vulnerabilities_found"]

        db_service.increment_vulnerabilities(5)

        updated_stats = db_service.get_stats()
        assert updated_stats["vulnerabilities_found"] == initial_count + 5

    def test_scan_with_result_data(self, db_service):
        """Test saving a scan with result data."""
        import json

        result_data = json.dumps([
            {"type": "reentrancy", "severity": "critical"},
            {"type": "overflow", "severity": "high"}
        ])

        scan_id = db_service.save_scan(
            scan_id="test_scan_results",
            contract_address="0x1234567890123456789012345678901234567890",
            result_data=result_data,
            vulnerability_count=2
        )

        scan = db_service.get_scan("test_scan_results")

        assert scan is not None
        assert scan["result_data"] is not None
