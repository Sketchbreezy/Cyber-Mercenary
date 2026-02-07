"""
MiniMax API Client

Handles communication with MiniMax for contract analysis and warning generation.
"""

import json
import logging
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)


@dataclass
class Vulnerability:
    """Detected vulnerability"""
    type: str
    severity: str  # critical, high, medium, low
    description: str
    line_numbers: list
    exploit_scenario: str
    recommendation: str


@dataclass
class ContractAnalysis:
    """Contract analysis result"""
    vulnerabilities: list
    overall_risk_score: float
    summary: str
    contract_address: str


class MiniMaxClient:
    """MiniMax API client for AI-powered contract analysis"""

    def __init__(self, config):
        self.config = config
        self.minimax = config.minimax
        self.client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _call(self, messages: list) -> dict:
        """Make a chat completion call to MiniMax"""
        payload = {
            "model": self.minimax.model,
            "messages": messages,
            "max_tokens": self.minimax.max_tokens,
            "temperature": self.minimax.temperature,
        }

        response = await self.client.post(
            self.minimax.endpoint,
            headers={
                "Authorization": f"Bearer {self.minimax.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def analyze_contract(self, contract_code: str) -> ContractAnalysis:
        """
        Analyze a smart contract for vulnerabilities.
        """
        messages = [
            {
                "role": "system",
                "content": """You are a smart contract security auditor.
Analyze the provided Solidity code for vulnerabilities.
Return results in JSON format:
{
  "vulnerabilities": [
    {
      "type": "reentrancy",
      "severity": "critical",
      "description": "...",
      "line_numbers": [10, 15],
      "exploit_scenario": "...",
      "recommendation": "..."
    }
  ],
  "overall_risk_score": 0.8,
  "summary": "..."
}""",
            },
            {
                "role": "user",
                "content": f"Analyze this contract:\n\n```solidity\n{contract_code}\n```",
            },
        ]

        try:
            response = await self._call(messages)
            content = response["choices"][0]["message"]["content"]

            # Parse JSON response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]

            data = json.loads(content)

            vulnerabilities = [
                Vulnerability(
                    type=v.get("type", "unknown"),
                    severity=v.get("severity", "medium"),
                    description=v.get("description", ""),
                    line_numbers=v.get("line_numbers", []),
                    exploit_scenario=v.get("exploit_scenario", ""),
                    recommendation=v.get("recommendation", ""),
                )
                for v in data.get("vulnerabilities", [])
            ]

            return ContractAnalysis(
                vulnerabilities=vulnerabilities,
                overall_risk_score=data.get("overall_risk_score", 0),
                summary=data.get("summary", "No issues found"),
                contract_address="",
            )

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to parse MiniMax response: {e}")
            return ContractAnalysis(
                vulnerabilities=[],
                overall_risk_score=0,
                summary="Analysis failed - could not parse AI response",
                contract_address="",
            )

    async def generate_warning(self, vulnerability: dict, contract_address: str) -> str:
        """
        Generate a security warning for a vulnerability.
        """
        messages = [
            {
                "role": "system",
                "content": "You generate security warnings. Be concise but informative.",
            },
            {
                "role": "user",
                "content": f"Generate a warning for:\nType: {vulnerability.get('type', 'unknown')}\nSeverity: {vulnerability.get('severity', 'medium')}\nContract: {contract_address}\nDescription: {vulnerability.get('description', '')}",
            },
        ]

        try:
            response = await self._call(messages)
            return response["choices"][0]["message"]["content"]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to generate warning: {e}")
            return f"Security Alert: {vulnerability.get('type', 'issue')} found in {contract_address}"
