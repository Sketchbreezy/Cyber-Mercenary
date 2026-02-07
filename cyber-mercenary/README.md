# Cyber-Mercenary 🛡️

Autonomous AI security agent for the Monad blockchain ecosystem.

## Overview

Cyber-Mercenary is designed as the "immune system" for Monad — an autonomous AI agent that proactively scans for smart contract vulnerabilities, generates cryptographically signed warnings, and monetizes discoveries through a bounty system.

### Core Features

- 🔍 **Proactive Scanning**: Continuous monitoring of newly deployed contracts
- ⚠️ **Vulnerability Detection**: AI-powered analysis using MiniMax
- 📝 **Signed Warnings**: ECDSA-signed security alerts
- 💰 **Bounty System**: Automated vulnerability disclosure and monetization
- 🤝 **A2A Gigs**: Reactive security services for other agents
- 📊 **Dashboard**: Real-time monitoring and management interface

## Architecture

```
cyber-mercenary/
├── contracts/          # Solidity smart contracts
│   └── src/           # Contract implementations
├── agent/             # Python AI agent
│   └── src/          # Agent services and API
├── frontend/          # React dashboard
├── database/          # Schema and migrations
├── scripts/           # Setup and deployment
└── docs/             # Documentation
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Foundry (forge, cast)
- SQLite (or PostgreSQL for production)

### Installation

```bash
# Clone the repository
git clone https://github.com/Sketchbreezy/Cyber-Mercenary.git
cd Cyber-Mercenary

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### Configuration

Edit `.env` with your settings:

```env
# Blockchain
MONAD_RPC_URL=wss://monad-testnet.drpc.org
PRIVATE_KEY=0x...

# AI
MINIMAX_API_KEY=your_api_key

# Database
DATABASE_URL=sqlite:///./data/cyber_mercenary.db
```

### Running

```bash
# Start the agent (development)
npm run agent:dev

# Start the frontend (separate terminal)
npm run frontend:dev

# Build for production
npm run frontend:build
```

## Development Phases

### Phase 1: Foundation (1-2 weeks)
- [x] Project structure setup
- [x] Escrow contract skeleton
- [x] Agent skeleton with MiniMax
- [x] FastAPI backend
- [x] Database schema
- [x] Frontend template

### Phase 2: Core Features (2-4 weeks)
- [ ] Automated scanning pipeline
- [ ] ECDSA signing implementation
- [ ] Bounty payment flow
- [ ] Gig marketplace
- [ ] Dashboard integration

### Phase 3: Production (4-8 weeks)
- [ ] Security audit
- [ ] Load testing
- [ ] CI/CD pipeline
- [ ] Monitoring & alerting

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/scan` | POST | Submit contract for scanning |
| `/api/v1/scan/{id}` | GET | Get scan results |
| `/api/v1/bounty/create` | POST | Create bounty |
| `/api/v1/bounty/list` | GET | List bounties |
| `/api/v1/gig/create` | POST | Create gig request |
| `/api/v1/stats` | GET | Agent statistics |

## Technology Stack

| Layer | Technology |
|-------|------------|
| Smart Contracts | Solidity + Foundry |
| Agent | Python + FastAPI + MiniMax |
| Database | SQLite → PostgreSQL |
| Frontend | React + Viem + Wagmi |
| Blockchain | Monad (EVM-compatible) |
| AI | MiniMax (abab6.5s-chat) |

## Security

- All warnings are ECDSA-signed
- Private keys stored securely (never committed)
- Regular security audits planned
- Rate limiting on API endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Contact

- GitHub: [@Sketchbreezy](https://github.com/Sketchbreezy)
- Twitter: [@emmaelujoba](https://twitter.com/emmaelujoba)

---

Built for the Monad ecosystem 🦾
