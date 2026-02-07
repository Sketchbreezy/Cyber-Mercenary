# MEMORY.md - Long-Term Memory

_Distilled wisdom, not raw logs. Built over time from daily files._

## 🚨 NEVER FORGET

- Wallet private key: `5241d075be5b9413d98e1dcf91ecabd60beb7ee833f3385cdab0315cb098fdec`
- Wallet address: `0x01A5584c6C15d4D210C93BbB18DF40EC77F7B59a`
- **NEVER deploy contracts without testnet funds**

---

## Cyber-Mercenary Project

### Architecture
- **Agent**: Python/FastAPI on port 8000
- **AI**: MiniMax model
- **Blockchain**: Monad testnet (Chain ID: 10143)
- **RPC**: `wss://monad-testnet.drpc.org`
- **Contracts**: Solidity with OpenZeppelin

### Contract Fixes (Lessons Learned)
- OpenZeppelin v5.5.0 requires Solidity ^0.8.24
- ReentrancyGuard moved from `security/` to `utils/`
- EIP712 is in `utils/cryptography/`
- Ownable constructor requires `initialOwner` argument
- Use `console.logAddress()` in Forge scripts, not `console.log(address)`

### Current Blocker
- Need testnet MON tokens from https://faucet.monad.xyz
- Cannot deploy Escrow contract without funds

---

## Preferences & Rules

- Use MiniMax for AI (configured)
- Prioritize simplicity over complexity
- Deploy to Monad testnet (Chain ID: 10143)
- Run on same VPS for compute

---

_Last updated: 2026-02-07_
