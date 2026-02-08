"""
Unit tests for the MiniMax Client.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import json


class TestMiniMaxClient:
    """Tests for the MiniMaxClient class."""

    @pytest.fixture
    def mock_minimax_response(self):
        """Mock MiniMax API response."""
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "vulnerabilities": [
                                {
                                    "type": "reentrancy",
                                    "severity": "critical",
                                    "description": "Reentrancy vulnerability detected in withdraw function",
                                    "line_numbers": [45, 52],
                                    "exploit_scenario": "Attacker can recursively call withdraw",
                                    "recommendation": "Use reentrancy guard or check-effects-interactions pattern"
                                },
                                {
                                    "type": "integer_overflow",
                                    "severity": "high",
                                    "description": "Potential integer overflow in arithmetic operation",
                                    "line_numbers": [120],
                                    "exploit_scenario": "Attacker manipulates values to cause overflow",
                                    "recommendation": "Use SafeMath library or Solidity 0.8+"
                                }
                            ],
                            "overall_risk_score": 0.85,
                            "summary": "Critical reentrancy vulnerability found. Immediate attention required."
                        })
                    }
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_analyze_contract_returns_analysis(self, mock_config, mock_minimax_response):
        """Test that analyze_contract returns a ContractAnalysis."""
        from services.minimax import MiniMaxClient, ContractAnalysis

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = mock_minimax_response

            client = MiniMaxClient(mock_config)
            result = await client.analyze_contract("0x60606040...")

            assert isinstance(result, ContractAnalysis)
            assert result.overall_risk_score == 0.85
            assert len(result.vulnerabilities) == 2
            assert result.vulnerabilities[0].type == "reentrancy"
            assert result.vulnerabilities[0].severity == "critical"

    @pytest.mark.asyncio
    async def test_analyze_contract_handles_api_error(self, mock_config):
        """Test that analyze_contract handles API errors gracefully."""
        from services.minimax import MiniMaxClient

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = {
                "error": {"message": "API rate limit exceeded"}
            }

            client = MiniMaxClient(mock_config)
            result = await client.analyze_contract("0x60606040...")

            assert result.overall_risk_score == 0
            assert "Analysis skipped" in result.summary

    @pytest.mark.asyncio
    async def test_analyze_contract_handles_json_error(self, mock_config):
        """Test that analyze_contract handles JSON parsing errors."""
        from services.minimax import MiniMaxClient

        invalid_response = {
            "choices": [
                {
                    "message": {
                        "content": "This is not valid JSON"
                    }
                }
            ]
        }

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = invalid_response

            client = MiniMaxClient(mock_config)
            result = await client.analyze_contract("0x60606040...")

            assert result.overall_risk_score == 0
            assert "could not parse" in result.summary.lower()

    @pytest.mark.asyncio
    async def test_analyze_contract_handles_empty_vulnerabilities(self, mock_config):
        """Test analysis with no vulnerabilities found."""
        from services.minimax import MiniMaxClient

        empty_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "vulnerabilities": [],
                            "overall_risk_score": 0.0,
                            "summary": "No vulnerabilities found. Contract appears safe."
                        })
                    }
                }
            ]
        }

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = empty_response

            client = MiniMaxClient(mock_config)
            result = await client.analyze_contract("0x60606040...")

            assert len(result.vulnerabilities) == 0
            assert result.overall_risk_score == 0.0
            assert "No vulnerabilities" in result.summary

    @pytest.mark.asyncio
    async def test_generate_warning(self, mock_config):
        """Test warning generation."""
        from services.minimax import MiniMaxClient

        warning_response = {
            "choices": [
                {
                    "message": {
                        "content": "Critical reentrancy vulnerability in withdraw function at line 45"
                    }
                }
            ]
        }

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = warning_response

            client = MiniMaxClient(mock_config)
            warning = await client.generate_warning(
                {"type": "reentrancy", "severity": "critical"},
                "0x1234567890123456789012345678901234567890"
            )

            assert "reentrancy" in warning.lower()
            assert len(warning) > 0

    @pytest.mark.asyncio
    async def test_generate_warning_fallback(self, mock_config):
        """Test warning generation fallback on error."""
        from services.minimax import MiniMaxClient

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Network error")

            client = MiniMaxClient(mock_config)
            warning = await client.generate_warning(
                {"type": "overflow", "severity": "high"},
                "0x1234567890123456789012345678901234567890"
            )

            assert "overflow" in warning.lower()

    @pytest.mark.asyncio
    async def test_client_uses_correct_endpoint(self, mock_config):
        """Test that client uses the correct API endpoint."""
        from services.minimax import MiniMaxClient

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = {
                "choices": [{"message": {"content": "{}"}}]
            }

            client = MiniMaxClient(mock_config)
            await client.analyze_contract("0x60606040")

            # Verify the correct endpoint was called
            call_args = mock_post.call_args
            assert call_args[0][0] == mock_config.minimax.endpoint

    @pytest.mark.asyncio
    async def test_client_includes_correct_headers(self, mock_config):
        """Test that client includes correct authentication headers."""
        from services.minimax import MiniMaxClient

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = {
                "choices": [{"message": {"content": "{}"}}]
            }

            client = MiniMaxClient(mock_config)
            await client.analyze_contract("0x60606040")

            # Verify headers
            headers = mock_post.call_args[1]["headers"]
            assert "Authorization" in headers
            assert headers["Authorization"] == f"Bearer {mock_config.minimax.api_key}"
            assert "Content-Type" in headers
            assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_client_closes_properly(self, mock_config):
        """Test that the client can be closed properly."""
        from services.minimax import MiniMaxClient

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock):
            client = MiniMaxClient(mock_config)
            await client.close()

            # Verify the HTTP client was closed
            assert client.client.is_closed
