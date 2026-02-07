# Cyber-Mercenary Project Schema

## Directory Structure

```
cyber-mercenary/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── .env.example
├── .gitignore
├── README.md
├── LICENSE
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── package.json
├── foundry.toml
├── hardhat.config.ts
├── tsconfig.json
├──/
├── contracts/
│   ├── src/
│   │   ├──/
│   │   │   ├── Escrow.sol
│   │   │   ├── BountyRegistry.sol
│   │   │   ├── A2APayment.sol
│   │   │   └── SignatureVerifier.sol
│   │   ├── interfaces/
│   │   │   ├── IEscrow.sol
│   │   │   ├── IBountyRegistry.sol
│   │   │   └── ISignatureVerifier.sol
│   │   ├── libraries/
│   │   │   └── ECDSAUtils.sol
│   │   └── test/
│   │       ├── Escrow.t.sol
│   │       └── Integration.t.sol
│   ├── script/
│   │   └── Deploy.s.sol
│   └── lib/
│       ├── forge-std/
│       └── openzeppelin-contracts/
├──/
├── agent/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                    # Agent entry point
│   │   ├── config.py                 # Configuration
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py            # Pydantic models
│   │   │   └── database.py           # Database models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── minimax.py            # MiniMax API integration
│   │   │   ├── scanner.py            # Contract scanner
│   │   │   ├── fuzzer.py             # Fuzzing engine
│   │   │   ├── signer.py             # ECDSA signing
│   │   │   └── notifier.py           # Warning delivery
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints.py          # REST endpoints
│   │   │   └── middleware.py         # Auth, rate limiting
│   │   ├── jobs/
│   │   │   ├── __init__.py
│   │   │   ├── scanner_job.py       # Periodic scanning
│   │   │   └── bounty_job.py        # Bounty processing
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logging.py
│   │       └── helpers.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_scanner.py
│   │   └── test_minimax.py
│   ├── prompts/
│   │   ├── analysis.txt              # Contract analysis prompt
│   │   ├── fuzzing.txt               # Fuzzing strategy prompt
│   │   └── warning.txt               # Warning generation prompt
│   ├── requirements.txt
│   └── Dockerfile
├──/
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── __init__.py
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── vite-env.d.ts
│   │   ├── api/
│   │   │   ├── client.ts             # Viem/Wagmi setup
│   │   │   └── endpoints.ts
│   │   ├── components/
│   │   │   ├── Layout.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Scanner.tsx
│   │   │   ├── Bounties.tsx
│   │   │   ├── Warnings.tsx
│   │   │   ├── Gigs.tsx
│   │   │   └── Stats.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Scanner.tsx
│   │   │   ├── Bounties.tsx
│   │   │   ├── Gigs.tsx
│   │   │   └── Settings.tsx
│   │   ├── hooks/
│   │   │   ├── useAgent.ts
│   │   │   ├── useContracts.ts
│   │   │   └── useScanner.ts
│   │   ├── context/
│   │   │   └── AppContext.tsx
│   │   ├── utils/
│   │   │   └── formatting.ts
│   │   ├── styles/
│   │   │   └── index.css
│   │   └── types/
│   │       └── index.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├──/
├── database/
│   ├── migrations/
│   │   ├── 001_init.sql
│   │   ├── 002_bounties.sql
│   │   └── 003_gigs.sql
│   ├── schema.sql
│   └── seed.sql
├──/
├── scripts/
│   ├── setup.sh                      # Initial setup script
│   ├── deploy.sh                     # Deployment script
│   ├── test.sh                       # Test runner
│   └── monitoring.sh                 # Health checks
├──/
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── contracts.md
│   └── deployment.md
├──/
└── .env.example
```

---

## Smart Contract Schema

### Escrow.sol

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

contract Escrow is Ownable, ReentrancyGuard, EIP712 {
    struct Bounty {
        uint256 id;
        address payable developer;
        uint256 amount;
        bool claimed;
        bool disputed;
        string ipfsHash;      // Encrypted report
        bytes signature;       // Agent's ECDSA signature
        uint256 createdAt;
        uint256 expiresAt;
    }

    mapping(uint256 => Bounty) public bounties;
    mapping(address => uint256[]) public developerBounties;
    
    uint256 public bountyCount;
    uint256 public constant MIN_BOUNTY = 0.001 ether;
    uint256 public constant FEE_PERCENT = 5;

    event BountyCreated(uint256 indexed id, address developer, uint256 amount);
    event BountyClaimed(uint256 indexed id, address claimer, uint256 amount);
    event BountyDisputed(uint256 indexed id);

    constructor() EIP712("CyberMercenary", "1") {}

    function createBounty(
        string memory ipfsHash,
        bytes memory signature,
        uint256 expiresIn
    ) external payable nonReentrant {
        require(msg.value >= MIN_BOUNTY, "Below minimum bounty");
        
        bountyCount++;
        uint256 fee = (msg.value * FEE_PERCENT) / 100;
        uint256 netAmount = msg.value - fee;

        bounties[bountyCount] = Bounty({
            id: bountyCount,
            developer: payable(msg.sender),
            amount: netAmount,
            claimed: false,
            disputed: false,
            ipfsHash: ipfsHash,
            signature: signature,
            createdAt: block.timestamp,
            expiresAt: block.timestamp + expiresIn
        });

        developerBounties[msg.sender].push(bountyCount);
        emit BountyCreated(bountyCount, msg.sender, netAmount);
    }

    function claimBounty(uint256 bountyId) external nonReentrant {
        Bounty storage bounty = bounties[bountyId];
        require(!bounty.claimed, "Already claimed");
        require(block.timestamp < bounty.expiresAt, "Expired");
        require(msg.sender == bounty.developer, "Not authorized");

        bounty.claimed = true;
        payable(msg.sender).transfer(bounty.amount);
        emit BountyClaimed(bountyId, msg.sender, bounty.amount);
    }

    function verifySignature(
        uint256 bountyId,
        bytes memory agentSignature
    ) external view returns (bool) {
        // ECDSA verification logic
    }
}
```

---

## Database Schema

### SQLite (MVP) → PostgreSQL (Production)

```sql
-- bounties table
CREATE TABLE bounties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_hash VARCHAR(66) NOT NULL UNIQUE,
    developer_address VARCHAR(42) NOT NULL,
    amount_wei BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'open', -- open, claimed, disputed, expired
    ipfs_report_hash VARCHAR(46),
    agent_signature VARCHAR(132),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    claimed_at TIMESTAMP,
    disputed_at TIMESTAMP
);

-- warnings table
CREATE TABLE warnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_address VARCHAR(42) NOT NULL,
    vulnerability_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    summary TEXT NOT NULL,
    full_report_ipfs VARCHAR(46),
    developer_contact VARCHAR(42),
    status VARCHAR(20) DEFAULT 'pending', -- pending, acknowledged, resolved
    bounty_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (bounty_id) REFERENCES bounties(id)
);

-- gigs table (A2A marketplace)
CREATE TABLE gigs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_agent VARCHAR(42) NOT NULL,
    provider_agent VARCHAR(42),
    task_type VARCHAR(50) NOT NULL, -- verification, simulation, calculation
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'open', -- open, assigned, completed, cancelled
    fee_wei BIGINT NOT NULL,
    escrow_id INTEGER,
    result_ipfs VARCHAR(46),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (escrow_id) REFERENCES bounties(id)
);

-- contracts_scanned table
CREATE TABLE contracts_scanned (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address VARCHAR(42) NOT NULL,
    chain_id INTEGER NOT NULL,
    bytecode_hash VARCHAR(66),
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vulnerabilities_found INTEGER DEFAULT 0,
    severity_distribution JSON, -- {"critical": 0, "high": 1, "medium": 2, "low": 5}
    PRIMARY KEY (address, chain_id)
);

-- agent_stats table
CREATE TABLE agent_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    contracts_scanned INTEGER DEFAULT 0,
    vulnerabilities_found INTEGER DEFAULT 0,
    bounties_earned_wei BIGINT DEFAULT 0,
    gigs_completed INTEGER DEFAULT 0,
    fees_earned_wei BIGINT DEFAULT 0
);
```

---

## API Schema (REST)

### Endpoints

```
POST /api/v1/scan              # Submit contract for scanning
GET  /api/v1/scan/{id}         # Get scan results
POST /api/v1/bounty/create     # Create bounty
POST /api/v1/bounty/claim      # Claim bounty
GET  /api/v1/bounty/list       # List available bounties
POST /api/v1/gig/create        # Create gig request
POST /api/v1/gig/accept        # Accept gig
POST /api/v1/gig/complete      # Complete gig
GET  /api/v1/warnings          # List warnings
GET  /api/v1/warnings/{id}     # Get warning details
GET  /api/v1/stats             # Agent statistics
```

### Request/Response Examples

**POST /api/v1/scan**

```json
{
  "contract_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f3bD5a",
  "chain_id": 143,
  "scan_depth": "standard" // light, standard, deep
}
```

**Response:**

```json
{
  "scan_id": "scan_abc123",
  "status": "queued",
  "estimated_time_seconds": 30
}
```

**GET /api/v1/scan/{id}**

```json
{
  "scan_id": "scan_abc123",
  "status": "completed",
  "vulnerabilities": [
    {
      "type": "reentrancy",
      "severity": "high",
      "description": "Potential reentrancy in withdraw function",
      "line_numbers": [45, 67, 89]
    }
  ],
  "risk_score": 7.5,
  "recommendation": "Add reentrancy guard"
}
```

---

## Agent Configuration (.env)

```bash
# Blockchain
MONAD_RPC_URL=https://api.alchemy.com/v2/YOUR_KEY
CHAIN_ID=143
ESCROW_CONTRACT_ADDRESS=0x...

# AI/MiniMax
MINIMAX_API_KEY=your_minimax_key
MINIMAX_ENDPOINT=https://api.minimax.chat/v1/text/chatcompletion_v2

# Database
DATABASE_URL=sqlite:///./data/cyber_mercenary.db

# Agent
AGENT_PRIVATE_KEY=0x...  # For signing warnings
AGENT_ADDRESS=0x...
SIGNING_INTERVAL_MINUTES=5

# Storage
IPFS_NODE_URL=http://127.0.0.1:5001
IPFS_GATEWAY=https://gateway.pinata.cloud

# Monitoring
LOG_LEVEL=INFO
METRICS_PORT=9090
```

---

## MiniMax Prompt Templates

### Contract Analysis

```
You are a smart contract security auditor. Analyze this Solidity code for vulnerabilities:

<contract_code>

Focus on:
1. Reentrancy vulnerabilities
2. Integer overflow/underflow
3. Access control issues
4. Front-running risks
5. Logic errors

Return a JSON object:
{
  "vulnerabilities": [
    {
      "type": "string",
      "severity": "critical|high|medium|low",
      "description": "string",
      "line_numbers": [numbers],
      "exploit_scenario": "string",
      "recommendation": "string"
    }
  ],
  "overall_risk_score": 0-10,
  "summary": "string"
}
```

### Warning Generation

```
Generate a signed security warning for this vulnerability:

Vulnerability: {type}
Severity: {severity}
Contract: {address}
Description: {description}

Create a concise warning message that:
1. Identifies the issue
2. Explains the risk without revealing full exploit
3. Mentions the bounty amount
4. Provides contact instructions

Sign this with ECDSA signature.
```

---

This schema covers the full stack. Want me to start building out any specific component?
