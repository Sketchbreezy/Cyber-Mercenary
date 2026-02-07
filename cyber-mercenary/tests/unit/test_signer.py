"""
Unit tests for the Signature Manager.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from eth_account import Account


class TestSignatureManager:
    """Tests for the SignatureManager class."""

    def test_sign_message_returns_signed_message(self, mock_config):
        """Test that sign_message returns a properly signed message."""
        from services.signer import SignatureManager, SignedMessage

        manager = SignatureManager(mock_config)

        # Sign a test message
        signed = manager.sign_message("Test message")

        # Verify the structure
        assert isinstance(signed, SignedMessage)
        assert signed.message == "Test message"
        assert signed.signature.startswith("0x")
        assert signed.hash.startswith("0x")
        assert len(signed.signature) == 132  # 65 bytes * 2 + 0x prefix
        assert len(signed.hash) == 66  # 32 bytes * 2 + 0x prefix

    def test_address_returns_correct_address(self, mock_config):
        """Test that address property returns the correct signer address."""
        from services.signer import SignatureManager

        manager = SignatureManager(mock_config)

        address = manager.address

        # Should be a valid Ethereum address
        assert address.startswith("0x")
        assert len(address) == 42

    def test_verify_valid_signature(self, mock_config):
        """Test that verify_signature returns True for a valid signature."""
        from services.signer import SignatureManager

        manager = SignatureManager(mock_config)

        # Sign a message
        signed = manager.sign_message("Test message to verify")

        # Verify the signature
        is_valid = manager.verify_signature(
            "Test message to verify",
            signed.signature,
            signed.signer_address
        )

        assert is_valid is True

    def test_verify_invalid_signature(self, mock_config):
        """Test that verify_signature returns False for an invalid signature."""
        from services.signer import SignatureManager

        manager = SignatureManager(mock_config)

        # Try to verify with a wrong signature
        is_valid = manager.verify_signature(
            "Test message",
            "0x" + "00" * 65,
            manager.address
        )

        assert is_valid is False

    def test_verify_wrong_address(self, mock_config):
        """Test that verify_signature returns False for wrong address."""
        from services.signer import SignatureManager

        manager = SignatureManager(mock_config)

        # Sign a message
        signed = manager.sign_message("Test message")

        # Verify with a different address
        is_valid = manager.verify_signature(
            "Test message",
            signed.signature,
            "0x" + "00" * 41
        )

        assert is_valid is False

    def test_sign_warning_creates_structured_message(self, mock_config):
        """Test that sign_warning creates a properly structured warning."""
        from services.signer import SignatureManager

        manager = SignatureManager(mock_config)

        # Sign a warning
        signed = manager.sign_warning("Critical reentrancy vulnerability found")

        # Verify the signature is valid
        assert signed.signature.startswith("0x")
        assert len(signed.signature) == 132

    def test_sign_message_without_private_key_raises(self):
        """Test that signing without a private key raises an error."""
        from services.signer import SignatureManager

        mock_config_no_key = Mock()
        mock_config_no_key.blockchain.private_key = None

        manager = SignatureManager(mock_config_no_key)

        with pytest.raises(ValueError, match="Private key not configured"):
            manager.sign_message("Test message")

    def test_create_delegation(self, mock_config):
        """Test that create_delegation returns delegation data and signature."""
        from services.signer import SignatureManager

        manager = SignatureManager(mock_config)

        # Create a delegation
        data, signature = manager.create_delegation(
            delegate_address="0x" + "ab" * 20,
            expiration=1234567890
        )

        # Verify the structure
        assert "delegate" in data
        assert "expiration" in data
        assert "nonce" in data
        assert isinstance(signature, type(mock_config))
        assert signature.signature.startswith("0x")
