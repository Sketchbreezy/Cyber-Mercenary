# Deploy
Deployment configurations for Cyber-Mercenary

## Quick Deploy (Docker)

### 1. Configure Environment
```bash
cp .env.example .env
nano .env
```

Set these required variables:
```env
MONAD_RPC_URL=wss://monad-testnet.drpc.org
MONAD_CHAIN_ID=10143
PRIVATE_KEY=0xyour_private_key
ESCROW_CONTRACT_ADDRESS=0xD2eCA8c096293BA3137bAeF47714f5Df1f6233cd
MINIMAX_API_KEY=sk-or-your-key
```

### 2. Deploy with Docker
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. Or use Docker Compose
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Production Deployment (Linux)

### 1. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3.12 python3-pip git

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure
```bash
sudo mkdir -p /opt/cyber-mercenary
sudo cp -r agent data logs deploy /opt/cyber-mercenary/
sudo chown -R appuser:appuser /opt/cyber-mercenary/

# Copy and edit environment
sudo cp /opt/cyber-mercenary/deploy/.env.example /opt/cyber-mercenary/.env
sudo nano /opt/cyber-mercenary/.env
```

### 3. Install Systemd Service
```bash
sudo cp /opt/cyber-mercenary/deploy/cyber-mercenary.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cyber-mercenary
sudo systemctl start cyber-mercenary
sudo systemctl status cyber-mercenary
```

### 4. Check Logs
```bash
journalctl -u cyber-mercenary -f
```

## Kubernetes Deployment

### 1. Create Namespace
```bash
kubectl create namespace cyber-mercenary
```

### 2. Apply Config
```bash
kubectl apply -f k8s/configmap.yaml -n cyber-mercenary
kubectl apply -f k8s/secret.yaml -n cyber-mercenary
```

### 3. Deploy
```bash
kubectl apply -f k8s/deployment.yaml -n cyber-mercenary
kubectl apply -f k8s/service.yaml -n cyber-mercenary
kubectl apply -f k8s/ingress.yaml -n cyber-mercenary
```

## Helm Deployment

```bash
helm install cyber-mercenary ./helm/cyber-mercenary/ \
  --namespace cyber-mercenary \
  --set image.repository=ghcr.io/sketchbreezy/cyber-mercenary \
  --set image.tag=latest \
  --set env.MONAD_RPC_URL=wss://monad-testnet.drpc.org \
  --set env.ESCROW_CONTRACT_ADDRESS=0xD2eCA8c096293BA3137bAeF47714f5Df1f6233cd
```

## Terraform Deployment

```bash
cd terraform
terraform init
terraform plan -var="rpc_url=wss://monad-testnet.drpc.org" -out=tfplan
terraform apply tfplan
```

## Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# Get agent address
curl http://localhost:8000/api/v1/agent/address

# Check stats
curl http://localhost:8000/api/v1/stats
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MONAD_RPC_URL` | Yes | `wss://monad-testnet.drpc.org` | Monad RPC endpoint |
| `MONAD_CHAIN_ID` | Yes | `10143` | Monad Testnet chain ID |
| `PRIVATE_KEY` | Yes | - | Wallet private key |
| `ESCROW_CONTRACT_ADDRESS` | Yes | - | Escrow contract address |
| `MINIMAX_API_KEY` | No | - | OpenRouter API key |
| `SCAN_INTERVAL_MINUTES` | No | `30` | Scan interval |
| `LOG_LEVEL` | No | `INFO` | Logging level |

## Troubleshooting

### Agent not starting
```bash
# Check logs
docker logs cyber-mercenary-agent
journalctl -u cyber-mercenary -f
```

### Blockchain connection failed
- Verify RPC URL is accessible
- Check firewall rules
- Ensure sufficient disk space

### Contract interaction failed
- Verify contract address is correct
- Check wallet has sufficient balance
- Verify chain ID matches
