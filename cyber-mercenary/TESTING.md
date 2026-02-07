## Testing

This document describes how to run tests for the Cyber-Mercenary project.

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Running Python tests |
| Foundry | Latest | Solidity compilation & testing |
| Git | Latest | Version control |

### Installation

```bash
# Install Python test dependencies
pip install -r requirements-test.txt

# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

### Running Python Tests

#### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_signer.py -v

# Run with coverage
pytest tests/unit/ --cov=agent/src --cov-report=term-missing
```

#### API Integration Tests

```bash
# Run API tests
pytest tests/api/ -v

# Run with verbose output
pytest tests/api/test_api.py -v -s
```

#### All Tests

```bash
# Run all tests
pytest tests/ -v --cov=agent/src
```

### Running Solidity Tests

#### Forge Tests

```bash
# Run all Solidity tests
forge test

# Run specific test contract
forge test --match-contract EscrowTest -vv

# Run with gas report
forge test --gas-report
```

#### Slither Static Analysis

```bash
# Install Slither
pip install slither-analyzer

# Run Slither
slither .
```

#### Echidna Fuzzing

```bash
# Install Echidna
curl -L https://github.com/crytic/echidna/releases/download/v2.1.0/echidna-v2.1.0-linux.tar.gz | tar xz
sudo mv echidna /usr/local/bin/

# Run Echidna
echidna-test contracts/test/Escrow.t.sol --config contracts/test/Echidna.yaml
```

### GitHub Actions

Tests are automatically run on every push and pull request:

| Job | Description | Trigger |
|-----|-------------|---------|
| `python-tests` | Run Python unit and integration tests | Every push/PR |
| `solidity-tests` | Run Forge tests and Slither analysis | Every push/PR |
| `api-integration` | Start API server and run integration tests | Every push/PR |
| `lint` | Check code formatting and style | Every push/PR |
| `security-scan` | Run Bandit, Safety, and pip-audit | Push to main |
| `deploy-staging` | Deploy to staging environment | Push to develop |
| `deploy-production` | Deploy to production | Push to main |

### Test Coverage

Current coverage targets:

- **Python code**: 80%+
- **Solidity code**: 90%+

View coverage reports:
```bash
# HTML coverage report
pytest tests/ --cov=agent/src --cov-report=html
open htmlcov/index.html
```

### Writing Tests

#### Python Tests

Tests are located in `tests/` directory:
- `tests/unit/` - Unit tests for individual components
- `tests/api/` - API integration tests
- `tests/conftest.py` - Shared fixtures

Example test structure:
```python
def test_feature(mock_config):
    """Test description."""
    from services.signer import SignatureManager
    
    manager = SignatureManager(mock_config)
    result = manager.sign_message("Test")
    
    assert result.signature.startswith("0x")
```

#### Solidity Tests

Tests are located in `contracts/test/` directory:
- `Escrow.t.sol` - Main test contract using Forge

Example test:
```solidity
function test_createBounty_success() public {
    vm.deal(developer, 1 ether);
    vm.prank(developer);
    escrow.createBounty{value: 0.01 ether}("QmTest", 1 hours);
    
    assertEq(escrow.bountyCount(), 1);
}
```

### CI/CD Pipeline

The CI/CD pipeline includes:
1. Code formatting checks (Black, Ruff, Forge fmt)
2. Static analysis (Slither, Bandit)
3. Unit tests (Python and Solidity)
4. Integration tests (API endpoints)
5. Security scanning (pip-audit, Safety)
6. Automated deployment (staging/production)

### Troubleshooting

#### Tests failing with import errors
```bash
# Ensure Python path is set correctly
export PYTHONPATH="${PYTHONPATH}:$(pwd)/agent/src"
```

#### Forge tests not compiling
```bash
# Reinstall dependencies
forge install
forge build --force
```

#### Port already in use during API tests
```bash
# Kill processes using port 8000
lsof -ti:8000 | xargs kill -9
```
