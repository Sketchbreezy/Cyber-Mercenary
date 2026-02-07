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
from pydantic import BaseModel

from config import Settings, MiniMaxConfig

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
    vulnerabilities: list[Vulnerability]
    overall_risk_score: float
    summary: str
    contract_address: str


class MiniMaxClient:
    """MiniMax API client for AI-powered contract analysis"""

    def __init__(self, config: Settings):
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

        Args:
            contract_code: The Solidity contract source code

        Returns:
            ContractAnalysis with vulnerabilities found
        """
        system_prompt = Path(__file__).parent.parent / "prompts" / "analysis.txt"
        if system_prompt.exists():
            with open(system_prompt) as f:
                system_content = f.read()
        else:
            system_content = """You are a smart contract security auditor.
Analyze the provided Solidity code for vulnerabilities.
Return results in JSON format with your findings."""

        messages = [
            {"role": "system", "content": system_content},
            {
                "role": "user",
                "content": f"Analyze this contract:\n\n```solidity\n{contract_code}\n```",
            },
        ]

        try:
            response = await self._call(messages)
            content = response["choices"][0]["message"]["content"]

            # Parse JSON response
            # Handle potential markdown formatting
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
                contract_address="",  # Set by caller
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse MiniMax response: {e}")
            return ContractAnalysis(
                vulnerabilities=[],
                overall_risk_score=0,
                summary="Analysis failed",
                contract_address="",
            )

    async def generate_warning(
        self,
        vulnerability: Vulnerability,
        contract_address: str,
    ) -> str:
        """
        Generate a security warning for a vulnerability.

        Args:
            vulnerability: The vulnerability details
            contract_address: Address of the vulnerable contract

        Returns:
            Warning message string
        """
        system_prompt = Path(__file__).parent.parent / "prompts" / "warning.txt"
        if system_prompt.exists():
            with open(system_prompt) as f:
                system_content = f.read()
        else:
            system_content = """You generate security warnings for smart contract vulnerabilities.
Be concise but informative. Include severity level without revealing full exploit details."""

        messages = [
            {"role": "system", "content": system_content},
            {
                "role": "user",
                "content": f"""Generate a security warning:
Vulnerability: {vulnerability.type}
Severity: {vulnerability.severity}
Contract: {contract_address}
Description: {vulnerability.description}""",
            },
        ]

        try:
            response = await self._call(messages)
            return response["choices"][0]["message"]["content"]
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to generate warning: {e}")
            return f"Security Alert: {vulnerability.type} found in {contract_address}"

    async def generate_fuzzing_strategy(
        self, contract_code: str, vulnerability_type: str
    ) -> dict:
        """
        Generate a fuzzing strategy for a specific vulnerability type.

        Args:
            contract_code: The contract code
            vulnerability_type: Type of vulnerability to target

        Returns:
            Fuzzing strategy dictionary
        """
        messages = [
            {
                "role": "system",
                "content": "You are a smart contract security tester. "
                "Generate fuzzing strategies to test for specific vulnerabilities.",
            },
            {
                "role": "user",
                "content": f"""Generate a fuzzing strategy for:
Contract:\n{contract_code}
Target Vulnerability: {vulnerability_type}

Provide:
1. Test function signature
2. Key assertions to check
3. Edge cases to explore
4. Expected outcomes""",
            },
        ]

        try:
            response = await self._call(messages)
            return {"strategy": response["choices"][0]["message"]["content"]}
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to generate fuzzing strategy: {e}")
            return {"strategy": "Fuzzing strategy generation failed"}
