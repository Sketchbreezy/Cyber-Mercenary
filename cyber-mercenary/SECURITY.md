# Cyber-Mercenary Security Documentation

## Security Overview

Cyber-Mercenary is an autonomous AI security agent for the Monad blockchain. This document outlines security practices, architecture, and audit preparation for the project.

## Security Architecture

### Core Security Principles

1. **Defense in Depth** - Multiple security layers protect the system
2. **Least Privilege** - Minimal permissions required for each component
3. **Secure by Default** - Conservative configuration choices
4. **Auditability** - All actions logged and traceable

### Security Controls

#### API Security
- **Rate Limiting**: Configured per-endpoint (see `agent/src/api/server.py`)
- **CORS**: Restricted origins (configure in production)
- **Input Validation**: Pydantic models with strict types
- **Security Headers**: Helmet middleware integration

#### Blockchain Security
- **Private Key Handling**: Environment variables only, never in code
- **Transaction Signing**: ECDSA signatures for all critical operations
- **Address Validation**: EIP-55 checksum validation
- **Chain ID Verification**: Prevents cross-chain replay attacks

#### Data Security
- **Database**: SQLite with file-level encryption support
- **Input Sanitization**: All user inputs validated and sanitized
- **Output Encoding**: JSON responses properly encoded

## Security Headers

All API responses include the following security headers:

| Header | Value | Purpose |
|--------|-------|---------|
| X-Content-Type-Options | nosniff | Prevent MIME type sniffing |
| X-Frame-Options | DENY | Prevent clickjacking |
| X-XSS-Protection | 1; mode=block | XSS filtering |
| Strict-Transport-Security | max-age=31536000; includeSubDomains | HSTS enforcement |
| Content-Security-Policy | default-src 'self' | CSP mitigation |
| Referrer-Policy | strict-origin-when-cross-origin | Referrer control |
| Permissions-Policy | geolocation=(), microphone=() | Feature restrictions |

## Authentication & Authorization

### Current State
- **Phase 2**: Open API with rate limiting only
- **Phase 3+**: API key authentication (planned)

### Future API Key Framework

```python
# Planned implementation in agent/src/api/security.py
class APIKeyAuth:
    """API Key authentication for future releases"""
    
    async def validate_key(self, key: str) -> bool:
        """Validate API key format and existence"""
        
    async def get_permissions(self, key: str) -> List[str]:
        """Get permissions for the API key"""
        
    async def check_rate_limit(self, key: str, endpoint: str) -> bool:
        """Check rate limit for API key"""
```

### Authorization Levels

| Level | Permissions | Use Case |
|-------|-------------|----------|
| Public | Read-only endpoints | General users |
| Basic | Scan, bounty create | Standard API users |
| Advanced | All endpoints + higher limits | Partners |
| Admin | Full access + management | System operators |

## Input Validation

### Contract Address Validation

```python
def validate_ethereum_address(address: str) -> bool:
    """Validate Ethereum address format and checksum"""
    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return False
    return web3.Web3.is_checksum_address(address)
```

### Request Validation

All endpoints use Pydantic models for input validation:

- `ScanRequest`: Contract address validation
- `BountyRequest`: Wei amount bounds checking
- `SignRequest`: Message length limits
- `VerifyRequest`: Signature format validation

## Threat Model

### Assets
1. **Private Keys**: Signing operations, treasury management
2. **API Keys**: External service access
3. **Scan Data**: Vulnerability information
4. **User Data**: Request logs, statistics

### Threats

| Threat | Impact | Mitigation |
|--------|--------|------------|
| Private key exposure | Critical | Environment variables, HSM support |
| API key theft | High | Rotation, scope limiting |
| SQL injection | High | Parameterized queries, ORM |
| XSS attacks | Medium | Output encoding, CSP |
| DoS attacks | Medium | Rate limiting, request size limits |
| Replay attacks | Medium | Nonce validation, chain ID checks |

### Attack Surfaces

1. **REST API**: Primary attack surface
2. **WebSocket**: Blockchain connection
3. **File Upload**: IPFS hash validation
4. **CLI**: Command injection prevention

## Vulnerability Disclosure

See [SECURITY.md](.github/SECURITY.md) for the vulnerability disclosure policy.

## Audit Checklist

See [audit-checklist.md](docs/audit-checklist.md) for the comprehensive security audit checklist.

## Compliance

### Smart Contract Security
- Slither analysis: `slither.config.json` configured
- Forge testing: Comprehensive test coverage
- Manual review: Required for major changes

### API Security
- OWASP API Security Top 10 alignment
- Rate limiting on all endpoints
- Input validation on all inputs

## Incident Response

### Severity Levels

| Level | Response Time | Examples |
|-------|---------------|----------|
| Critical | 1 hour | Private key exposed, smart contract bug |
| High | 4 hours | API vulnerability, data breach |
| Medium | 24 hours | XSS, information disclosure |
| Low | 72 hours | Documentation issues, minor bugs |

### Response Steps

1. **Triage**: Assess severity and impact
2. **Contain**: Limit damage (rotate keys, disable endpoints)
3. **Remediate**: Fix vulnerability
4. **Recover**: Restore service
5. **Document**: Record incident and lessons learned

## Security Contacts

- **Primary**: Security team via GitHub Issues
- **Critical**: Emergency contact (see contract deployer)
- **PGP**: Available on request

## Dependencies Security

### Trusted Dependencies
- FastAPI: Web framework
- Pydantic: Data validation
- SlowApi: Rate limiting
- Web3.py: Blockchain interaction
- OpenZeppelin: Smart contract libraries

### Vulnerability Monitoring
- Dependabot enabled for GitHub
- Manual review for critical updates
- Pin to specific versions in production

## Security Testing

### Automated Tests
```bash
# Run security tests
pytest tests/ -v --tb=short

# Static analysis
flake8 agent/src/ --select=E,F,W --max-line-length=100

# Type checking
mypy agent/src/
```

### Manual Testing
- Penetration testing before major releases
- Code review for all changes
- Third-party audits for smart contracts

## Deployment Security

### Production Checklist
- [ ] Environment variables set
- [ ] CORS origins restricted
- [ ] Rate limits configured
- [ ] Logging enabled
- [ ] Monitoring active
- [ ] Backups configured
- [ ] SSL/TLS configured
- [ ] WAF enabled

### Environment Configuration
```bash
# Required for production
PRIVATE_KEY=<encrypted>
DATABASE_URL=<secure connection>
MONAD_RPC_URL=<wss://...>
MINIMAX_API_KEY=<encrypted>
```

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-07 | Initial security documentation |
