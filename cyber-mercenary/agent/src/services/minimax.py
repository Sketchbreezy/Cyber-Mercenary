"""
MiniMax API Client (OpenRouter format)

Uses OpenRouter to access MiniMax models with free credits.
OpenRouter is OpenAI-compatible.
"""

import json
import logging
from typing import Optional
from dataclasses import dataclass

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
    """MiniMax API client via OpenRouter (OpenAI-compatible format)"""

    def __init__(self, config):
        self.config = config
        self.minimax = config.minimax
        self.client = httpx.AsyncClient(timeout=120.0)

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _call(self, messages: list, system_prompt: str = None) -> dict:
        """Make a chat completion call via OpenRouter (OpenAI format)"""
        payload = {
            "model": self.minimax.model,
            "messages": messages,
            "max_tokens": self.minimax.max_tokens,
            "temperature": self.minimax.temperature,
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = await self.client.post(
                self.minimax.endpoint,
                headers={
                    "Authorization": f"Bearer {self.minimax.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/Sketchbreezy/Cyber-Mercenary",
                    "X-Title": "Cyber-Mercenary",
                },
                json=payload,
                timeout=120.0,
            )

            data = response.json()

            # Check for OpenRouter errors
            if "error" in data:
                logger.error(f"OpenRouter API error: {data['error'].get('message', 'Unknown error')}")
                return {"error": data["error"].get("message", "API error")}

            return data

        except Exception as e:
            logger.error(f"OpenRouter API call failed: {e}")
            return {"error": str(e)}

    async def analyze_contract(self, contract_code: str) -> ContractAnalysis:
        """
        Analyze a smart contract for vulnerabilities.
        """
        system_prompt = """You are a smart contract security auditor.
Analyze the provided Solidity code for vulnerabilities.
Return results in JSON format:
{
  "vulnerabilities": [
    {
      "type": "reentrancy",
      "severity": "critical",
      "description": "Description of the vulnerability",
      "line_numbers": [10, 15],
      "exploit_scenario": "How an attacker could exploit this",
      "recommendation": "How to fix it"
    }
  ],
  "overall_risk_score": 0.8,
  "summary": "Brief summary of findings"
}"""

        user_message = f"Analyze this Solidity contract for security vulnerabilities:\n\n```solidity\n{contract_code}\n```\n\nReturn ONLY the JSON response, no markdown formatting."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            response = await self._call(messages)

            # Check for errors
            if "error" in response:
                logger.error(f"OpenRouter error: {response['error']}")
                return ContractAnalysis(
                    vulnerabilities=[],
                    overall_risk_score=0,
                    summary=f"Analysis skipped: {response['error']}",
                    contract_address="",
                )

            # Parse OpenAI-style response format
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Parse JSON from the text content
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]

            data = json.loads(content)

            vulnerabilities = []
            for v in data.get("vulnerabilities", []):
                vulnerabilities.append(Vulnerability(
                    type=v.get("type", "unknown"),
                    severity=v.get("severity", "medium"),
                    description=v.get("description", ""),
                    line_numbers=v.get("line_numbers", []),
                    exploit_scenario=v.get("exploit_scenario", ""),
                    recommendation=v.get("recommendation", ""),
                ))

            return ContractAnalysis(
                vulnerabilities=vulnerabilities,
                overall_risk_score=data.get("overall_risk_score", 0),
                summary=data.get("summary", "No issues found"),
                contract_address="",
            )

        except (json.JSONDecodeError, KeyError, TypeError, IndexError) as e:
            logger.error(f"Failed to parse OpenRouter response: {e}")
            return ContractAnalysis(
                vulnerabilities=[],
                overall_risk_score=0,
                summary="Analysis failed - could not parse AI response",
                contract_address="",
            )

    async def generate_warning(self, vulnerability: dict, contract_address: str) -> str:
        """Generate a security warning for a vulnerability."""
        messages = [
            {
                "role": "user",
                "content": f"Generate a concise security warning (1-2 sentences) for:\nType: {vulnerability.get('type', 'unknown')}\nSeverity: {vulnerability.get('severity', 'medium')}\nContract: {contract_address}\n\nReturn only the warning text, no markdown."
            },
        ]

        try:
            response = await self._call(messages)

            if "error" in response:
                return f"Security Alert: {vulnerability.get('type', 'issue')} found in {contract_address}"

            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content.strip() if content else f"Security Alert: {vulnerability.get('type', 'issue')} found"

        except Exception as e:
            logger.error(f"Failed to generate warning: {e}")
            return f"Security Alert: {vulnerability.get('type', 'issue')} found in {contract_address}"
