#!/bin/bash

# Cyber-Mercenary Setup Script
# Initializes the project and installs dependencies

set -e

echo "🚀 Cyber-Mercenary Setup"
echo "========================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo ""
echo "📋 Checking prerequisites..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"

# Check Node.js version (optional)
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION found"
else
    echo -e "${YELLOW}⚠️ Node.js not found (optional for frontend)${NC}"
fi

# Check Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is required but not installed${NC}"
    exit 1
fi
echo "✅ Git found"

# Create data directory
echo ""
echo "📁 Creating data directory..."
mkdir -p data

# Install Python dependencies
echo ""
echo "🐍 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    python3 -m pip install -q -r requirements.txt
    echo "✅ Python dependencies installed"
else
    echo -e "${YELLOW}⚠️ requirements.txt not found, skipping${NC}"
fi

# Install Node.js dependencies (if package.json exists)
echo ""
echo "📦 Installing Node.js dependencies..."
if [ -f "package.json" ]; then
    if ! command -v npm &> /dev/null; then
        echo -e "${YELLOW}⚠️ npm not found, skipping Node.js deps${NC}"
    else
        npm install --silent
        echo "✅ Node.js dependencies installed"
    fi
else
    echo -e "${YELLOW}⚠️ package.json not found, skipping${NC}"
fi

# Install Foundry
echo ""
echo "🔨 Checking Foundry..."
if ! command -v forge &> /dev/null; then
    echo "Installing Foundry..."
    curl -L https://foundry.paradigm.xyz | bash
    export PATH="$HOME/.foundry/bin:$PATH"
    foundryup
fi
echo "✅ Foundry found: $(forge --version)"

# Initialize Foundry dependencies
echo ""
echo "📦 Installing Foundry dependencies..."
if [ -d "contracts/lib" ]; then
    forge install --no-git
    echo "✅ Foundry dependencies installed"
else
    echo -e "${YELLOW}⚠️ contracts/lib directory not found${NC}"
fi

# Copy environment file
echo ""
echo "🔧 Setting up environment..."
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env from template"
    echo -e "${YELLOW}⚠️ Please edit .env with your configuration${NC}"
else
    echo -e "${YELLOW}⚠️ .env already exists or .env.example not found${NC}"
fi

# Initialize database
echo ""
echo "🗄️ Initializing database..."
if [ -f "database/schema.sql" ]; then
    sqlite3 data/cyber_mercenary.db < database/schema.sql
    echo "✅ Database initialized"
else
    echo -e "${YELLOW}⚠️ database/schema.sql not found${NC}"
fi

# Run migrations (if using Alembic)
echo ""
echo "📊 Running migrations..."
if [ -d "database/migrations" ]; then
    if command -v alembic &> /dev/null; then
        alembic upgrade head
        echo "✅ Migrations complete"
    else
        echo -e "${YELLOW}⚠️ Alembic not found, skipping migrations${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ database/migrations not found${NC}"
fi

# Summary
echo ""
echo "========================"
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Add your Monad RPC URL"
echo "3. Add your MiniMax API key"
echo "4. Add your wallet private key"
echo "5. Run: npm run agent:dev (for development)"
echo ""
echo "For more info, see: docs/architecture.md"
