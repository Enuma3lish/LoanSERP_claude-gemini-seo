#!/bin/bash
# Start all backend services (Django + FastAPI)

echo "========================================="
echo "LoanSERP Backend Services Startup"
echo "========================================="
echo ""
echo "This script will start:"
echo "  1. Django Backend (port 8000)"
echo "  2. LLM Broker/FastAPI (port 9001)"
echo ""
echo "Make sure Docker services (Postgres + Redis) are running!"
echo "Run: cd docker && docker-compose up -d"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping all services..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Django in background
echo "Starting Django Backend..."
"$SCRIPT_DIR/start-backend.sh" &
DJANGO_PID=$!

# Wait a bit for Django to start
sleep 3

# Start FastAPI in background
echo ""
echo "Starting LLM Broker..."
"$SCRIPT_DIR/start-llm-broker.sh" &
FASTAPI_PID=$!

# Wait for both processes
echo ""
echo "========================================="
echo "All services started!"
echo "========================================="
echo "Django Backend: http://localhost:8000/api/"
echo "LLM Broker:     http://localhost:9001/v1/"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

wait
