#!/bin/bash
# =============================================================================
# LoanSERP Docker Startup Script
# =============================================================================
# This script helps you start the LoanSERP application with Docker
# =============================================================================

set -e  # Exit on error

echo "========================================"
echo "  LoanSERP Docker Startup"
echo "========================================"
echo ""

# -----------------------------------------------------------------------------
# Step 1: Check if .env files exist
# -----------------------------------------------------------------------------
echo "[1/5] Checking environment configuration..."

if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found in root directory"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "   ✅ Created .env - PLEASE EDIT IT WITH YOUR ACTUAL VALUES!"
    echo ""
fi

if [ ! -f "geo_LLM_infra/llm_broker/.env" ]; then
    echo "⚠️  .env file not found in geo_LLM_infra/llm_broker/"
    echo "   Creating from .env.example..."
    cp geo_LLM_infra/llm_broker/.env.example geo_LLM_infra/llm_broker/.env
    echo "   ✅ Created geo_LLM_infra/llm_broker/.env - PLEASE EDIT IT WITH YOUR ACTUAL VALUES!"
    echo ""
fi

# -----------------------------------------------------------------------------
# Step 2: Check if secrets directory exists (for GSC credentials)
# -----------------------------------------------------------------------------
echo "[2/5] Checking secrets directory..."

if [ ! -d "secrets" ]; then
    echo "   Creating secrets directory..."
    mkdir -p secrets
    echo "   ✅ Created secrets/ directory"
    echo "   ⚠️  Remember to add your GSC credentials to secrets/"
    echo ""
fi

# -----------------------------------------------------------------------------
# Step 3: Create data directories
# -----------------------------------------------------------------------------
echo "[3/5] Creating data directories..."

mkdir -p data/postgres
mkdir -p data/redis

echo "   ✅ Data directories created"
echo ""

# -----------------------------------------------------------------------------
# Step 4: Build and start services
# -----------------------------------------------------------------------------
echo "[4/5] Building Docker images (this may take a few minutes)..."
echo ""

docker compose build --no-cache

echo ""
echo "[5/5] Starting services..."
echo ""

docker compose up -d

echo ""
echo "========================================"
echo "  🚀 LoanSERP Started Successfully!"
echo "========================================"
echo ""
echo "Services running:"
echo "  - Frontend:    http://localhost"
echo "  - Backend API: http://localhost:8000"
echo "  - LLM Broker:  http://localhost:9001"
echo "  - PostgreSQL:  localhost:5432"
echo "  - Redis:       localhost:6379"
echo ""
echo "Useful commands:"
echo "  - View logs:        docker compose logs -f"
echo "  - View status:      docker compose ps"
echo "  - Stop services:    docker compose down"
echo "  - Restart service:  docker compose restart <service-name>"
echo ""
echo "⚠️  IMPORTANT: Make sure you've configured:"
echo "  1. .env file with your database and API credentials"
echo "  2. geo_LLM_infra/llm_broker/.env with LLM API keys"
echo "  3. secrets/ directory with GSC credentials (if using GSC integration)"
echo ""
