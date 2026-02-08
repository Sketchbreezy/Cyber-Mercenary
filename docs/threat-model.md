# Cyber-Mercenary Threat Model

## Document Information

| Property | Value |
|----------|-------|
| Version | 1.0 |
| Date | 2026-02-07 |
| Author | Security Team |
| Classification | Internal |

## Executive Summary

Cyber-Mercenary is an autonomous AI security agent that scans smart contracts on the Monad blockchain for vulnerabilities. This threat model identifies and analyzes potential security threats to the system.

## System Overview

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Cyber-Mercenary System                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   REST API  │  │  Scanner    │  │  MiniMax AI Engine  │ │
│  │  (FastAPI)  │  │  Service    │  │  (External)         │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                     │            │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────────┴──────────┐ │
│  │   Database  │  │   Signer    │  │   Blockchain Node   │ │
│  │  (SQLite)   │  │   Service   │  │   (Monad RPC)       │ │
│  └─────────────┘  └──────┬──────┘  └─────────────────────┘ │
│                          │                                │
│                 ┌────────┴────────┐                       │
│                 │   Private Key   │                       │
│                 │   (HSM/Env)     │                       │
│                 └─────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. User → API: Scan request with contract address
2. API → Scanner: Validate and queue scan
3. Scanner → Blockchain: Fetch contract bytecode
4. Scanner → AI: Analyze bytecode for vulnerabilities
5. Signer → Blockchain: Sign results (if vulnerabilities found)
6. API → User: Return scan results

## Assets

### Primary Assets

| Asset | Classification | Owner | Location |
|-------|----------------|-------|----------|
| Private Key | Critical | System | Environment/HSM |
| API Keys (MiniMax) | High | System | Environment |
| Scan Results | Medium | System | Database |
| User Requests | Low | Users | Logs |
| Contract Bytecode | Low | Public | Blockchain |

### Secondary Assets

| Asset | Classification | Description |
|-------|----------------|-------------|
| Database | Medium | SQLite file |
| Configuration | Medium | .env file |
| Logs | Low | JSON log files |
| Tests | Low | Test files |

## Trust Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                     External Trust Zone                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Users      │  │   Blockchain │  │   MiniMax API    │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │             │
│    Untrusted         Semi-Trusted          Untrusted         │
└─────────────────────┬───────────────────────┬────────────────┘
                      │                       │
              ┌───────┴───────┐       ┌───────┴───────┐
              │   API Layer   │       │  AI Service   │
              │   (Limited    │       │   Adapter     │
              │    Trust)     │       │  (Validated)  │
              └───────┬───────┘       └───────────────┘
                      │
              ┌───────┴───────┐
              │  Core System  │
              │   (Trusted)   │
              └───────────────┘
```

## Threat Analysis

### STRIDE Analysis

| Threat | Asset | Attack Vector | Impact | Mitigation |
|--------|-------|---------------|--------|------------|
| Spoofing | API requests | Fake identity | Medium | Rate limiting, future API keys |
| Tampering | Scan results | Modify data | High | ECDSA signatures |
| Repudiation | User actions | Deny actions | Medium | Audit logging |
| Information Disclosure | Private key | Log exposure | Critical | Environment variables |
| Denial of Service | API availability | Request flood | Medium | Rate limiting |
| Elevation of Privilege | API access | Bypass auth | High | Future API key auth |

### Threat Scenarios

#### T1: Private Key Exposure
- **Severity**: Critical
- **Vector**: Log files, environment dump, memory dump
- **Impact**: Complete system compromise, fund theft
- **Likelihood**: Low (with proper practices)
- **Mitigation**:
  - Use environment variables only
  - Never log private key
  - Use HSM in production
  - Implement key rotation

#### T2: Smart Contract Vulnerability
- **Severity**: High
- **Vector**: Malicious contract bytecode
- **Impact**: AI analysis bypass, false results
- **Likelihood**: Medium
- **Mitigation**:
  - Sandbox analysis environment
  - Bytecode size limits
  - Timeout on analysis
  - Validate AI responses

#### T3: API Abuse (DoS)
- **Severity**: Medium
- **Vector**: Excessive scan requests
- **Impact**: Service degradation
- **Likelihood**: High
- **Mitigation**:
  - Rate limiting (100/minute, 10/minute for scans)
  - Request size limits
  - Background task queuing

#### T4: SQL Injection
- **Severity**: High
- **Vector**: User input in database queries
- **Impact**: Data theft, data corruption
- **Likelihood**: Low (using ORM)
- **Mitigation**:
  - Pydantic validation
  - Parameterized queries
  - Input sanitization

#### T5: XSS via API Responses
- **Severity**: Medium
- **Vector**: Malicious input in responses
- **Impact**: User browser compromise
- **Likelihood**: Low (JSON API)
- **Mitigation**:
  - Content-Type headers
  - Output encoding
  - CSP headers

#### T6: Replay Attack
- **Severity**: Medium
- **Vector**: Replay signed transactions
- **Impact**: Unauthorized transactions
- **Likelihood**: Medium
- **Mitigation**:
  - Nonce management
  - Chain ID verification
  - Transaction expiration

#### T7: AI API Compromise
- **Severity**: Medium
- **Vector**: Malicious AI responses
- **Impact**: Incorrect vulnerability reports
- **Likelihood**: Low
- **Mitigation**:
  - Response validation
  - Multiple AI providers
  - Manual review for critical contracts

#### T8: Information Disclosure
- **Severity**: Medium
- **Vector**: Verbose error messages
- **Impact**: System information leak
- **Likelihood**: Medium
- **Mitigation**:
  - Sanitized error messages
  - Generic responses in production
  - Remove server headers

## Attack Surface

### External Attack Surface

| Component | Protocol | Exposure | Risk Level |
|-----------|----------|----------|------------|
| REST API | HTTPS | Public | Medium |
| WebSocket | WSS | Public | Low |
| RPC Node | WSS | Semi-public | Low |

### Internal Attack Surface

| Component | Access | Risk Level |
|-----------|--------|------------|
| Database | Local | Low |
| Configuration | Local | Medium |
| Private Key | Restricted | Critical |

## Security Controls

### Implemented Controls

| Control | Type | Strength |
|---------|------|----------|
| Rate Limiting | Preventive | Strong |
| Input Validation | Preventive | Strong |
| CORS | Defense-in-depth | Moderate |
| Security Headers | Defense-in-depth | Strong |
| ECDSA Signatures | Detective/Corrective | Strong |
| Audit Logging | Detective | Moderate |

### Planned Controls

| Control | Type | Timeline |
|---------|------|----------|
| API Key Authentication | Preventive | Phase 4 |
| HSM Integration | Preventive | Phase 4 |
| WAF | Preventive | Phase 4 |
| SIEM Integration | Detective | Phase 4 |

## Risk Assessment Summary

| Risk | Severity | Mitigation Status |
|------|----------|-------------------|
| Private Key Exposure | Critical | ✅ Controlled |
| Smart Contract Vuln | High | ⚠️ Partially Mitigated |
| API Abuse | Medium | ✅ Controlled |
| SQL Injection | High | ✅ Controlled |
| XSS | Medium | ✅ Controlled |
| Replay Attack | Medium | ⚠️ Partially Mitigated |
| AI API Compromise | Medium | ⚠️ Partially Mitigated |
| Info Disclosure | Medium | ✅ Controlled |

## Recommendations

### Short-term (Phase 3)
1. Implement HSM for key storage
2. Add API key authentication
3. Enhance error message sanitization
4. Implement request signing for critical operations

### Medium-term (Phase 4)
1. Deploy WAF
2. Implement SIEM
3. Add anomaly detection
4. Regular penetration testing

### Long-term
1. Zero-trust architecture
2. Automated security scanning
3. Continuous security monitoring
4. Third-party security audits

## Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| STRIDE | Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation |
| CSP | Content Security Policy |
| HSM | Hardware Security Module |
| WAF | Web Application Firewall |
| SIEM | Security Information and Event Management |

### B. References

- OWASP Top 10 (2021)
- OWASP API Security Top 10
- NIST Cybersecurity Framework
- Ethereum Smart Contract Best Practices

### C. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-07 | Security Team | Initial release |
