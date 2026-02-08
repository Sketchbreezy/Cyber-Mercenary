#!/bin/bash
# Cyber-Mercenary Deployment Script
# Deploys agent to Monad Testnet

set -e

echo "🚀 Deploying Cyber-Mercenary to Monad Testnet..."
echo "================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="cyber-mercenary-agent"
IMAGE_NAME="cyber-mercenary:latest"
RPC_URL="${MONAD_RPC_URL:-wss://monad-testnet.drpc.org}"
CONTRACT_ADDR="${ESCROW_CONTRACT_ADDRESS}"

# Check prerequisites
echo ""
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi
echo "✅ Docker is installed"

# Check environment variables
echo ""
echo "🔐 Checking environment variables..."

if [ -z "$PRIVATE_KEY" ]; then
    echo -e "${RED}❌ PRIVATE_KEY is not set${NC}"
    exit 1
fi
echo "✅ PRIVATE_KEY is configured"

if [ -z "$ESCROW_CONTRACT_ADDRESS" ]; then
    echo -e "${YELLOW}⚠️ ESCROW_CONTRACT_ADDRESS not set, will use default${NC}"
fi

# Check blockchain connection
echo ""
echo "🔗 Checking blockchain connection..."
if curl -s --max-time 10 "$RPC_URL" | grep -q "error"; then
    echo -e "${RED}❌ Cannot connect to RPC: $RPC_URL${NC}"
    exit 1
fi
echo "✅ Connected to Monad Testnet"

# Build Docker image
echo ""
echo "🔨 Building Docker image..."
docker build -t "$IMAGE_NAME" .
echo "✅ Docker image built"

# Stop existing container
echo ""
echo "🛑 Stopping existing container..."
if docker ps -a --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo "✅ Removed existing container"
fi

# Run new container
echo ""
echo "🚀 Starting new container..."
docker run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -p 8000:8000 \
    -e MONAD_RPC_URL="$RPC_URL" \
    -e MONAD_CHAIN_ID=10143 \
    -e PRIVATE_KEY="$PRIVATE_KEY" \
    -e MINIMAX_API_KEY="${MINIMAX_API_KEY:-}" \
    -e ESCROW_CONTRACT_ADDRESS="$CONTRACT_ADDR" \
    -e SCAN_INTERVAL_MINUTES=30 \
    -e LOG_LEVEL=INFO \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/logs:/app/logs" \
    "$IMAGE_NAME"

# Wait for startup
echo ""
echo "⏳ Waiting for agent to start..."
sleep 5

# Health check
echo ""
echo "🏥 Running health check..."
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Agent is healthy!${NC}"
    echo ""
    echo "================================================"
    echo "🎉 Cyber-Mercenary deployed successfully!"
    echo ""
    echo "📡 Agent API: http://localhost:8000"
    echo "📊 Health: http://localhost:8000/health"
    echo "📈 Stats: http://localhost:8000/api/v1/stats"
    echo ""
    echo "🔗 Contract: $CONTRACT_ADDR"
    echo "🌐 Network: Monad Testnet (Chain ID: 10143)"
    echo "================================================"
else
    echo -e "${RED}❌ Agent health check failed${NC}"
    echo "Logs:"
    docker logs "$CONTAINER_NAME" --tail 50
    exit 1
fi
