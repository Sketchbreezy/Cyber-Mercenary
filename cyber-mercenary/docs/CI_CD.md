# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Cyber-Mercenary project.

## Table of Contents

1. [Overview](#overview)
2. [Workflows](#workflows)
3. [CI Pipeline (ci.yml)](#ci-pipeline-ciyml)
4. [Security Pipeline (security.yml)](#security-pipeline-securityyml)
5. [Deploy Pipeline (deploy.yml)](#deploy-pipeline-deployyml)
6. [Docker Support](#docker-support)
7. [Kubernetes Deployment](#kubernetes-deployment)
8. [Helm Charts](#helm-charts)
9. [Terraform Infrastructure](#terraform-infrastructure)
10. [Local Development](#local-development)
11. [Environment Variables](#environment-variables)

---

## Overview

The Cyber-Mercenary CI/CD pipeline consists of three main GitHub Actions workflows:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **CI Pipeline** | Push/PR to main/develop | Build, test, and lint |
| **Security Pipeline** | Push to main, weekly, PR | Vulnerability scanning |
| **Deploy Pipeline** | Push to main, releases | Docker build and deployment |

---

## Workflows

### CI Pipeline (ci.yml)

The main CI pipeline runs on every push and pull request to `main` and `develop` branches.

#### Jobs

1. **lint-and-format**
   - Checks Python formatting with Black
   - Lints Python with Ruff
   - Type checks with mypy
   - Validates Solidity formatting with forge fmt

2. **tests** (matrix: unit, integration, contract)
   - **unit**: Python unit tests with pytest and coverage
   - **integration**: API integration tests
   - **contract**: Solidity contract compilation and Forge tests

3. **build-verification**
   - Verifies Python build
   - Validates Solidity compilation
   - Checks dependency tree

#### Example Usage

```bash
# Run locally
pip install black ruff mypy pytest
black --check agent/src/
ruff check agent/src/
mypy agent/src/
pytest tests/ -v --cov=agent/src
forge build
forge test
```

---

### Security Pipeline (security.yml)

The security pipeline runs comprehensive vulnerability scanning on every push to `main`, weekly scheduled scans, and PRs.

#### Jobs

1. **bandit-scan**: Python security scanning with Bandit
2. **safety-check**: Python dependency vulnerability scanning
3. **pip-audit**: pip dependency audit with SARIF output
4. **owasp-dependency-check**: OWASP dependency vulnerability check
5. **slither-analysis**: Solidity smart contract static analysis
6. **trivy-scan**: Container image vulnerability scanning
7. **security-report**: Summary report of all scans

#### SARIF Output

Security results are uploaded as SARIF files to GitHub's Security tab:

```yaml
- name: Upload SARIF results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: bandit.sarif
```

#### Example Usage

```bash
# Run locally
pip install bandit safety pip-audit
bandit -r agent/src/
safety check
pip-audit
pip install slither-analyzer
slither .
```

---

### Deploy Pipeline (deploy.yml)

The deployment pipeline builds Docker images, scans for vulnerabilities, and deploys to multiple environments.

#### Jobs

1. **build-and-scan**
   - Builds Docker image
   - Runs Trivy container scan
   - Outputs image digest

2. **push-image**
   - Pushes image to GitHub Container Registry
   - Runs on main branch push

3. **deploy-staging**
   - Deploys to staging environment
   - Uses kubectl with kubeconfig

4. **deploy-production**
   - Deploys to production
   - Requires manual approval
   - Runs kubectl rollout

5. **terraform-deploy**
   - Applies Terraform configuration
   - Creates cloud infrastructure

6. **helm-deploy**
   - Deploys using Helm charts
   - Installs/updates release

#### Image Tagging

Images are tagged with:
- SHA commit hash
- Branch name
- `latest` (for main branch)

```yaml
tags: |
  type=sha
  type=ref,event=branch
  type=raw,value=latest,enable={{is_default_branch}}
```

---

## Docker Support

### Dockerfile

The project includes a multi-stage Docker build for the Cyber-Mercenary agent.

```dockerfile
FROM python:3.12-slim-bookworm
WORKDIR /app
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy application
COPY agent/ ./agent/
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "agent.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run

```bash
# Build image
docker build -t cyber-mercenary:latest .

# Run container
docker run -p 8000:8000 \
  -e MONAD_RPC_URL="https://monad-testnet.drpc.org" \
  -e ESCROW_CONTRACT_ADDRESS="0x..." \
  cyber-mercenary:latest
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f cyber-mercenary

# Stop services
docker-compose down
```

#### Services

| Service | Description | Port |
|---------|-------------|------|
| cyber-mercenary | Main agent | 8000 |
| postgres | Database (optional) | 5432 |
| redis | Cache (optional) | 6379 |
| prometheus | Metrics | 9090 |
| grafana | Dashboards | 3000 |

---

## Kubernetes Deployment

### Files

| File | Purpose |
|------|---------|
| `k8s/deployment.yaml` | Main deployment with replicas, resources, probes |
| `k8s/service.yaml` | ClusterIP and headless services |
| `k8s/ingress.yaml` | Ingress with TLS configuration |

### Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl rollout status deployment/cyber-mercenary

# View pods
kubectl get pods -l app=cyber-mercenary

# View logs
kubectl logs -l app=cyber-mercenary --tail=100
```

### Resource Configuration

```yaml
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi
```

### Health Checks

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

---

## Helm Charts

### Install Helm Chart

```bash
# Add Helm repository (if published)
helm repo add cyber-mercenary https://charts.cyber-mercenary.io

# Install chart
helm install cyber-mercenary cyber-mercenary/cyber-mercenary \
  --namespace production \
  --create-namespace

# Upgrade chart
helm upgrade cyber-mercenary cyber-mercenary/cyber-mercenary \
  --namespace production
```

### Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | 3 |
| `image.repository` | Container image | `ghcr.io/sketchbreezy/cyber-mercenary` |
| `image.tag` | Image tag | `latest` |
| `service.type` | Service type | `ClusterIP` |
| `ingress.enabled` | Enable ingress | `true` |
| `autoscaling.enabled` | Enable HPA | `true` |
| `persistentVolume.enabled` | Enable PVC | `true` |

### Horizontal Pod Autoscaler

```yaml
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

---

## Terraform Infrastructure

### Initialize Terraform

```bash
cd terraform
terraform init
```

### Apply Infrastructure

```bash
# Create terraform.tfvars
cp terraform.tfvars.example terraform.tfvars

# Plan changes
terraform plan -var="image_tag=v2.0.0"

# Apply changes
terraform apply -var="image_tag=v2.0.0"
```

### Resources Created

| Resource | Description |
|----------|-------------|
| `kubernetes_namespace` | Production and monitoring namespaces |
| `kubernetes_deployment` | Cyber-Mercenary deployment |
| `kubernetes_service` | ClusterIP service |
| `kubernetes_ingress` | NGINX ingress with TLS |
| `kubernetes_secret` | Application secrets |

---

## Local Development

### Quick Start

```bash
# Clone and setup
git clone https://github.com/Sketchbreezy/Cyber-Mercenary.git
cd Cyber-Mercenary

# Install dependencies
pip install -r requirements.txt

# Run with Docker Compose
docker-compose up -d

# Run tests
pytest tests/ -v
```

### Environment Variables

Create `.env` file:

```env
# Blockchain
MONAD_RPC_URL=https://monad-testnet.drpc.org
MONAD_CHAIN_ID=10143
PRIVATE_KEY=0x...

# AI
MINIMAX_API_KEY=sk-or-v1-...
MINIMAX_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
MINIMAX_MODEL=minimax/minimax-m2.1

# Contract
ESCROW_CONTRACT_ADDRESS=0x...
```

### Running CI Locally

```bash
# Install act (GitHub Actions runner)
brew install act

# Run CI workflow locally
act -j lint-and-format
act -j tests
```

---

## Environment Variables

### Required Variables

| Variable | Description | Source |
|----------|-------------|--------|
| `MONAD_RPC_URL` | Monad RPC endpoint | `.env`, secrets |
| `MONAD_CHAIN_ID` | Monad chain ID | `10143` |
| `ESCROW_CONTRACT_ADDRESS` | Escrow contract address | `.env`, secrets |
| `MINIMAX_API_KEY` | MiniMax API key | `.env`, secrets |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MINIMAX_ENDPOINT` | AI API endpoint | OpenRouter |
| `MINIMAX_MODEL` | AI model | `minimax/minimax-m2.1` |
| `PYTHONUNBUFFERED` | Python output | `1` |
| `DATABASE_URL` | PostgreSQL connection | SQLite |
| `REDIS_URL` | Redis connection | None |

---

## Security Considerations

### Secrets Management

- Use GitHub Secrets for sensitive values
- Use Kubernetes Secrets for deployments
- Rotate API keys regularly
- Never commit secrets to version control

### Container Security

- Run as non-root user
- Use read-only root filesystem
- Drop unnecessary capabilities
- Scan images before deployment

### Network Security

- Use TLS for all external communication
- Restrict ingress/egress rules
- Use service mesh for mTLS (optional)

---

## Monitoring

### Prometheus Metrics

The agent exposes Prometheus metrics on `/metrics`:

```python
from prometheus_client import Counter, Histogram

REQUESTS = Counter('cyber_mercenary_requests_total', 'Total requests')
SCANS = Counter('cyber_mercenary_scans_total', 'Total scans')
SCAN_DURATION = Histogram('cyber_mercenary_scan_duration', 'Scan duration')
```

### Grafana Dashboards

Pre-built dashboards are available in `monitoring/grafana/`:

```bash
# Access Grafana
open http://localhost:3000
# Login: admin/admin
```

---

## Troubleshooting

### CI Pipeline

```bash
# Check workflow runs
gh run list

# View workflow logs
gh run view <run-id> --log
```

### Docker Issues

```bash
# Build with no cache
docker build --no-cache -t cyber-mercenary .

# View container logs
docker logs cyber-mercenary-agent
```

### Kubernetes Issues

```bash
# Describe pod
kubectl describe pod <pod-name>

# View pod events
kubectl get events --sort-by='.metadata.creationTimestamp'
```

---

## Contributing

1. Ensure all CI checks pass before opening PR
2. Add tests for new functionality
3. Update documentation as needed
4. Follow code style guidelines (Black, Ruff)
5. Run security scans before merging

---

## License

MIT License - see LICENSE file for details.
