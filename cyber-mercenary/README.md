# 🛡️ Cyber-Mercenary

Autonomous AI Security Agent for the Monad Blockchain Ecosystem

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Solidity 0.8.24](https://img.shields.io/badge/Solidity-0.8.24-purple.svg)](https://soliditylang.org/)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Core Features](#core-features)
3. [Architecture](#architecture)
4. [Development Phases](#development-phases)
5. [Quick Start](#quick-start)
6. [Configuration Guide](#configuration-guide)
7. [API Documentation](#api-documentation)
8. [Smart Contracts](#smart-contracts)
9. [AI Integration](#ai-integration)
10. [Database Schema](#database-schema)
11. [Deployment](#deployment)
12. [Security](#security)
13. [Contributing](#contributing)
14. [License](#license)

---

## Overview

Cyber-Mercenary is an **autonomous AI security agent** designed to be the "immune system" for the Monad blockchain. It proactively scans smart contracts for vulnerabilities, generates cryptographically signed warnings, and monetizes discoveries through an integrated bounty system.

### The Vision

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cyber-Mercenary Agent                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │
│  │  Scanner    │──▶│    AI       │──▶│   ECDSA Signer      │   │
│  │  (Web3.py)  │   │ (MiniMax)   │   │   (eth-account)     │   │
│  └─────────────┘   └─────────────┘   └─────────────────────┘   │
│         │                                       │               │
│         ▼                                       ▼               │
│  ┌─────────────┐                       ┌─────────────┐         │
│  │  Database   │◀──────────────────────│   Warnings  │         │
│  │  (SQLite)   │                       │   (Signed)  │         │
│  └─────────────┘                       └─────────────┘         │
│         │                                       │               │
│         ▼                                       ▼               │
│  ┌─────────────────────────────────────────────────────┐       │
│  │              Bounty & Gig Marketplace               │       │
│  │              (Escrow Contract)                       │       │
│  └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| 🔍 **Proactive Scanning** | Continuous monitoring of newly deployed contracts | ✅ Active |
| 🤖 **AI Analysis** | MiniMax-powered vulnerability detection | ✅ Active |
| ✍️ **ECDSA Signing** | Cryptographically signed security warnings | ✅ Active |
| 💰 **Bounty System** | Automated vulnerability disclosure and monetization | ✅ Deployed |
| 🗂️ **SQLite Database** | Persistent storage for scans and statistics | ✅ Active |
| 🌐 **REST API** | FastAPI-powered endpoints for integration | ✅ Active |
| ⚡ **Background Processing** | Async scan queue for non-blocking operations | ✅ Active |

---

## Architecture

```
cyber-mercenary/
├── contracts/              # Solidity smart contracts
│   ├── src/
│   │   ├── Escrow.sol     # Bounty payment contract
│   │   └── Deploy.s.sol   # Foundry deployment script
│   ├── lib/               # OpenZeppelin contracts
│   └── test/              # Contract tests
│
├── agent/                  # Python AI agent
│   └── src/
│       ├── main.py         # Agent entry point
│       ├── config.py       # Configuration management
│       ├── api/
│       │   └── server.py   # FastAPI REST endpoints
│       └── services/
│           ├── minimax.py  # MiniMax AI client
│           ├── scanner.py  # Blockchain scanner
│           ├── signer.py   # ECDSA signature manager
│           └── database.py # SQLite persistence
│
├── data/                   # Database and logs
│   └── cyber_mercenary.db  # SQLite database
│
├── memory/                 # Session memory (OpenClaw)
│   └── YYYY-MM-DD.md
│
├── docs/                   # Documentation
├── .env                    # Environment variables (gitignored)
├── .env.example            # Environment template
├── foundry.toml           # Foundry configuration
├── pyproject.toml         # Python dependencies
└── README.md             # This file
```

---

## Development Phases

### Phase 1: Foundation ✅ COMPLETE

**Duration:** Week 1-2

#### Objectives
- [x] Project structure setup
- [x] Escrow contract skeleton
- [x] Agent skeleton with configuration
- [x] FastAPI backend with basic endpoints
- [x] Database schema design

#### Deliverables
```
✅ contracts/src/Escrow.sol
✅ agent/src/main.py
✅ agent/src/config.py
✅ agent/src/api/server.py
✅ .env.example
```

#### Key Files Created

| File | Purpose |
|------|---------|
| `contracts/src/Escrow.sol` | Bounty payment contract with ECDSA verification |
| `agent/src/main.py` | Agent entry point with .env loading |
| `agent/src/config.py` | Configuration management with dataclasses |
| `agent/src/api/server.py` | FastAPI server with health, scan, stats endpoints |

#### Contract Deployment
```
Escrow: 0x705a3a2be44Ad0b00f291314a6818EDF9d77071a
Network: Monad Testnet (Chain ID: 10143)
RPC: wss://monad-testnet.drpc.org
```

---

### Phase 2: Core Features ✅ COMPLETE

**Duration:** Week 2-4

#### Objectives
- [x] MiniMax AI client integration (via OpenRouter)
- [x] ECDSA signing/verification system
- [x] SQLite database for persistence
- [x] Background scan processing
- [x] Comprehensive API endpoints

#### MiniMax Integration

```python
# agent/src/services/minimax.py
from httpx import AsyncClient

class MiniMaxClient:
    def __init__(self, config):
        self.endpoint = config.minimax.endpoint  # OpenRouter
        self.model = config.minimax.model        # minimax/minimax-m2.1
        self.api_key = config.minimax.api_key
        self.client = AsyncClient(timeout=120.0)

    async def analyze_contract(self, bytecode: str) -> ContractAnalysis:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a smart contract security auditor..."},
                {"role": "user", "content": f"Analyze this bytecode:\n\n{bytecode}"}
            ],
            "max_tokens": 4096,
            "temperature": 0.7,
        }
        response = await self.client.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        return self._parse_response(response.json())
```

#### ECDSA Signing

```python
# agent/src/services/signer.py
from eth_account import Account
from eth_account.messages import encode_defunct

class SignatureManager:
    def sign_message(self, message: str) -> SignedMessage:
        account = Account.from_key(self.private_key)
        encoded = encode_defunct(text=message)
        signed = account.sign_message(encoded)
        return SignedMessage(
            message=message,
            signature=signed.signature.hex(),
            hash=Web3.keccak(text=message).hex(),
            signer_address=account.address,
        )
```

#### Database Service

```python
# agent/src/services/database.py
class DatabaseService:
    def save_scan(self, scan_id: str, address: str, status: str, 
                  risk_score: float = 0, vulns: int = 0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scans (scan_id, contract_address, status, 
                              risk_score, vulnerability_count)
            VALUES (?, ?, ?, ?, ?)
        """, (scan_id, address, status, risk_score, vulns))
        conn.commit()
        conn.close()
```

#### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Agent health check |
| `/` | GET | Root info |
| `/api/v1/scan` | POST | Submit contract for AI scanning |
| `/api/v1/scan/{id}` | GET | Get scan results |
| `/api/v1/scans` | GET | List all scans |
| `/api/v1/bounty/create` | POST | Create bounty on-chain |
| `/api/v1/bounty/{id}` | GET | Get bounty status |
| `/api/v1/bounty/{id}/dispute` | POST | File a dispute |
| `/api/v1/bounty/{id}/resolve` | POST | Resolve a dispute |
| `/api/v1/bounty/{id}/claim` | POST | Claim a bounty |
| `/api/v1/bounty/{id}/report` | POST | Submit report with signature |
| `/api/v1/stats` | GET | Agent statistics |
| `/api/v1/agent/address` | GET | Agent's signing address |
| `/api/v1/sign` | POST | Sign a message (ECDSA) |
| `/api/v1/verify` | POST | Verify a signature |

#### Test Results
```
✅ Health Check: {"phase":"2","services":"ready"}
✅ ECDSA Sign: Signature generated and verified
✅ AI Scan: Analyzed bytecode via OpenRouter
✅ Database: 7 contracts scanned, 8 vulnerabilities found
✅ Bounty Create: On-chain transaction
✅ Bounty Claim: On-chain transaction
✅ Dispute/Resolve: On-chain transactions
```

---

### Phase 2: Full Bounty System Integration ✅

#### On-Chain Bounty Operations

**File:** `agent/src/services/scanner.py`

```python
from web3 import Web3
from typing import Tuple

# Escrow Contract ABI (full implementation)
ESCROW_ABI = [
    {"name": "createBounty", "type": "function", "stateMutability": "payable"},
    {"name": "claimBounty", "type": "function", "stateMutability": "nonpayable"},
    {"name": "disputeBounty", "type": "function", "stateMutability": "nonpayable"},
    {"name": "resolveDispute", "type": "function", "stateMutability": "nonpayable"},
    {"name": "submitReport", "type": "function", "stateMutability": "nonpayable"},
    {"name": "bounties", "type": "function", "stateMutability": "view"}
]

class ContractScanner:
    def __init__(self, config):
        self.config = config
        self.w3 = Web3(Web3.HTTPProvider(config.blockchain.monad_rpc_url))
        self._escrow_contract = None

    def _get_escrow_contract(self):
        if self._escrow_contract is None and self.config.contracts.escrow:
            self._escrow_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.config.contracts.escrow),
                abi=ESCROW_ABI
            )
        return self._escrow_contract

    def _sign_and_send(self, tx) -> str:
        signed = self.w3.eth.account.sign_transaction(tx, self.config.blockchain.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()

    async def create_bounty(self, amount_wei: int, ipfs_hash: str, 
                           expires_in: int = 86400) -> Tuple[int, str]:
        """Create a new bounty on-chain"""
        escrow = self._get_escrow_contract()
        if not escrow:
            return (1, "0xplaceholder")

        agent_addr = Web3().eth.account.from_key(self.config.blockchain.private_key).address
        
        tx = escrow.functions.createBounty(ipfs_hash, expires_in).build_transaction({
            'from': agent_addr,
            'value': amount_wei,
            'gas': 300000,
            'nonce': self.w3.eth.get_transaction_count(agent_addr),
            'chainId': self.config.blockchain.monad_chain_id
        })

        tx_hash = self._sign_and_send(tx)
        bounty_id = escrow.functions.bountyCount().call()
        
        logger.info(f"✅ Bounty created: ID={bounty_id}, Tx={tx_hash[:16]}...")
        return (bounty_id, tx_hash)

    async def claim_bounty(self, bounty_id: int) -> str:
        """Claim a bounty on-chain"""
        escrow = self._get_escrow_contract()
        agent_addr = Web3().eth.account.from_key(self.config.blockchain.private_key).address
        
        tx = escrow.functions.claimBounty(bounty_id).build_transaction({
            'from': agent_addr,
            'gas': 300000,
            'nonce': self.w3.eth.get_transaction_count(agent_addr),
            'chainId': self.config.blockchain.monad_chain_id
        })

        return self._sign_and_send(tx)

    async def dispute_bounty(self, bounty_id: int) -> str:
        """File a dispute on-chain"""
        escrow = self._get_escrow_contract()
        agent_addr = Web3().eth.account.from_key(self.config.blockchain.private_key).address
        
        tx = escrow.functions.disputeBounty(bounty_id).build_transaction({
            'from': agent_addr,
            'gas': 300000,
            'nonce': self.w3.eth.get_transaction_count(agent_addr),
            'chainId': self.config.blockchain.monad_chain_id
        })

        return self._sign_and_send(tx)

    async def resolve_dispute(self, bounty_id: int, reward_developer: bool) -> str:
        """Resolve a dispute on-chain"""
        escrow = self._get_escrow_contract()
        agent_addr = Web3().eth.account.from_key(self.config.blockchain.private_key).address
        
        tx = escrow.functions.resolveDispute(bounty_id, reward_developer).build_transaction({
            'from': agent_addr,
            'gas': 300000,
            'nonce': self.w3.eth.get_transaction_count(agent_addr),
            'chainId': self.config.blockchain.monad_chain_id
        })

        return self._sign_and_send(tx)

    async def get_bounty_status(self, bounty_id: int) -> dict:
        """Get bounty status from blockchain"""
        escrow = self._get_escrow_contract()
        if not escrow:
            return {"id": bounty_id, "status": "unknown"}

        bounty = escrow.functions.bounties(bounty_id).call()
        return {
            "id": bounty_id,
            "developer": bounty[1],
            "amount": bounty[2],
            "claimed": bounty[3],
            "disputed": bounty[4],
            "expiresAt": bounty[8],
            "status": "disputed" if bounty[4] else ("claimed" if bounty[3] else "active")
        }
```

#### Bounty API Endpoints

```python
# agent/src/api/server.py

@app.post("/api/v1/bounty/create")
async def create_bounty(request: BountyRequest):
    bounty_id, tx_hash = await scanner.create_bounty(
        request.amount_wei, request.ipfs_hash, request.expires_in
    )
    db.save_bounty(bounty_id, None, request.amount_wei, "created")
    return {"bounty_id": bounty_id, "tx_hash": tx_hash, "status": "created"}

@app.post("/api/v1/bounty/{bounty_id}/dispute")
async def dispute_bounty(request: BountyDisputeRequest):
    tx_hash = await scanner.dispute_bounty(request.bounty_id)
    return {"bounty_id": request.bounty_id, "tx_hash": tx_hash, "status": "disputed"}

@app.post("/api/v1/bounty/{bounty_id}/resolve")
async def resolve_dispute(request: BountyResolveRequest):
    tx_hash = await scanner.resolve_dispute(request.bounty_id, request.reward_developer)
    return {"bounty_id": request.bounty_id, "tx_hash": tx_hash, "reward_developer": request.reward_developer, "status": "resolved"}

@app.post("/api/v1/bounty/{bounty_id}/claim")
async def claim_bounty(bounty_id: int):
    tx_hash = await scanner.claim_bounty(bounty_id)
    return {"bounty_id": bounty_id, "tx_hash": tx_hash, "status": "claimed"}
```

---

### Phase 3: Production (Upcoming)

**Duration:** Week 4-8

#### Objectives
- [ ] Frontend dashboard (React + Viem + Wagmi)
- [ ] Gig marketplace for A2A services
- [ ] IPFS integration for report storage
- [ ] Security audit
- [ ] Load testing
- [ ] CI/CD pipeline
- [ ] Monitoring & alerting

#### Planned Features
- Real-time dashboard
- Multi-chain support
- Advanced vulnerability patterns
- Automated exploit verification
- Agent-to-agent gig economy

---

## Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Agent runtime |
| Foundry | Latest | Solidity compilation & deployment |
| Git | Latest | Version control |

### Installation

```bash
# Clone the repository
git clone https://github.com/Sketchbreezy/Cyber-Mercenary.git
cd Cyber-Mercenary

# Install Python dependencies
pip install -r requirements.txt

# Install Foundry (if not already installed)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Compile contracts
forge build
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your settings
nano .env
```

#### Required Configuration

```env
# Blockchain
MONAD_RPC_URL=wss://monad-testnet.drpc.org
MONAD_CHAIN_ID=10143
PRIVATE_KEY=0xYourPrivateKey

# AI (OpenRouter - $1 free credits)
MINIMAX_API_KEY=sk-or-your-openrouter-key
MINIMAX_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
MINIMAX_MODEL=minimax/minimax-m2.1

# Contract
ESCROW_CONTRACT_ADDRESS=0x705a3a2be44Ad0b00f291314a6818EDF9d77071a
```

### Running the Agent

```bash
# Start the agent
python3 agent/src/main.py

# Agent will start on http://localhost:8000
```

### Testing

```bash
# Health check
curl http://localhost:8000/health

# Submit a scan
curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"contract_address": "0x705a3a2be44Ad0b00f291314a6818EDF9d77071a"}'

# Get stats
curl http://localhost:8000/api/v1/stats
```

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "agent": "CyberMercenary",
  "phase": "2",
  "services": "ready"
}
```

#### Submit Scan
```http
POST /api/v1/scan
Content-Type: application/json

{
  "contract_address": "0x...",
  "chain_id": 10143
}
```
**Response:**
```json
{
  "scan_id": "scan_abc123",
  "status": "queued",
  "contract_address": "0x...",
  "vulnerabilities": [],
  "risk_score": 0.0,
  "warning": null,
  "signature": null
}
```

#### Get Scan Status
```http
GET /api/v1/scan/{scan_id}
```
**Response:**
```json
{
  "scan_id": "scan_abc123",
  "status": "completed",
  "contract_address": "0x...",
  "risk_score": 0.6,
  "vulnerabilities": [...],
  "created_at": "2026-02-07T12:00:00"
}
```

#### Sign Message
```http
POST /api/v1/sign
Content-Type: application/json

{
  "message": "Security warning text"
}
```
**Response:**
```json
{
  "message": "Security warning text",
  "signature": "0x...",
  "hash": "0x...",
  "signer": "0x01A5584c6C15d4D210C93BbB18DF40EC77F7B59a"
}
```

#### Get Statistics
```http
GET /api/v1/stats
```
**Response:**
```json
{
  "contracts_scanned": 7,
  "vulnerabilities_found": 8,
  "bounties_earned": 0,
  "gigs_completed": 0
}
```

---

## Smart Contracts

### Escrow Contract

**Location:** `contracts/src/Escrow.sol`

**Features:**
- Bounty creation with ETH
- Developer claim functionality
- ECDSA signature verification
- Dispute resolution
- Platform fee collection (5%)

**Solidity Version:** 0.8.24

**Key Functions:**
```solidity
function createBounty(string memory ipfsHash, uint256 expiresIn) external payable
function submitReport(uint256 bountyId, bytes memory signature) external
function claimBounty(uint256 bountyId) external nonReentrant
function disputeBounty(uint256 bountyId) external
function resolveDispute(uint256 bountyId, bool rewardDeveloper) external onlyOwner
```

**Deployment:**
```
Deployed to: 0x705a3a2be44Ad0b00f291314a6818EDF9d77071a
Network: Monad Testnet (Chain ID: 10143)
```

### Deployment Script

**Location:** `contracts/src/Deploy.s.sol`

```solidity
contract DeployEscrow is Script {
    function run() external {
        vm.startBroadcast();
        Escrow escrow = new Escrow();
        console.logAddress(address(escrow));
        vm.stopBroadcast();
    }
}
```

**Deploy Command:**
```bash
forge script contracts/src/Deploy.s.sol:DeployEscrow \
  --rpc-url https://monad-testnet.drpc.org \
  --private-key $PRIVATE_KEY \
  --broadcast
```

---

## AI Integration

### MiniMax via OpenRouter

We use **MiniMax M2.1** model via OpenRouter for AI-powered contract analysis.

#### Why OpenRouter?
- $1 free credits for new accounts
- OpenAI-compatible API format
- No credit card required
- Supports MiniMax M2.1

#### Configuration
```env
MINIMAX_API_KEY=sk-or-your-key
MINIMAX_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
MINIMAX_MODEL=minimax/minimax-m2.1
MINIMAX_MAX_TOKENS=4096
MINIMAX_TEMPERATURE=0.7
```

#### Getting Free API Key
1. Visit https://openrouter.ai/keys
2. Sign up/login (free)
3. Create a new API key
4. Copy the key (starts with `sk-or-v1-`)

#### Analysis Prompt
```python
SYSTEM_PROMPT = """You are a smart contract security auditor.
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
}"""
```

---

## Database Schema

### Scans Table
```sql
CREATE TABLE scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id TEXT UNIQUE NOT NULL,
    contract_address TEXT NOT NULL,
    chain_id INTEGER DEFAULT 10143,
    status TEXT DEFAULT 'queued',
    risk_score REAL DEFAULT 0,
    vulnerability_count INTEGER DEFAULT 0,
    result_data TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Bounties Table
```sql
CREATE TABLE bounties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bounty_id INTEGER NOT NULL,
    contract_address TEXT,
    amount_wei INTEGER DEFAULT 0,
    status TEXT DEFAULT 'created',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    claimed_at TEXT
);
```

### Statistics Table
```sql
CREATE TABLE stats (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    contracts_scanned INTEGER DEFAULT 0,
    vulnerabilities_found INTEGER DEFAULT 0,
    bounties_earned REAL DEFAULT 0,
    gigs_completed INTEGER DEFAULT 0,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## Deployment

### Development
```bash
# Run agent
python3 agent/src/main.py

# Agent runs on port 8000
```

### Production (TODO)
```bash
# Build frontend
npm run build

# Run with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker agent.src.main:app

# Or use Docker
docker build -t cyber-mercenary .
docker run -p 8000:8000 cyber-mercenary
```

---

## Security

### Key Security Measures

1. **Private Key Management**
   - Stored in `.env` (gitignored)
   - Never committed to version control
   - Used only for signing

2. **ECDSA Signatures**
   - All warnings are cryptographically signed
   - Signature verification endpoint available
   - Prevents spoofing attacks

3. **API Security**
   - Rate limiting (TODO)
   - Input validation with Pydantic
   - CORS configuration

4. **Audit Roadmap**
   - Smart contract audit (Phase 3)
   - Python security review
   - Penetration testing

---

## Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Team
- [@Sketchbreezy](https://github.com/Sketchbreezy) - Lead Developer
- [@Ayomide-R](https://github.com/Ayomide-R) - Collaborator

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Monad](https://www.monad.xyz/) - Blockchain infrastructure
- [MiniMax](https://minimax.chat/) - AI model
- [OpenRouter](https://openrouter.ai/) - API routing
- [OpenZeppelin](https://openzeppelin.com/) - Smart contract libraries
- [Foundry](https://book.getfoundry.sh/) - Solidity tooling
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework

---

**Built for the Monad Hackathon 2026** 🦾

*Autonomous security for the decentralized future.*
