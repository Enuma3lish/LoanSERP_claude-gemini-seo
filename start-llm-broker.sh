#!/bin/bash
# Start LLM Broker (FastAPI) server

# Change to llm_broker directory
cd "$(dirname "$0")/geo_LLM_infra/llm_broker"

# Load environment variables from geo_LLM_infra/.env
export $(cat ../.env | grep -v '^#' | xargs)

echo "========================================="
echo "Starting LLM Broker (FastAPI) Server"
echo "========================================="
echo "Server will run on: http://localhost:9001"
echo "API endpoints available at: http://localhost:9001/v1/"
echo ""

# Start FastAPI server
echo "Starting LLM Broker..."
uvicorn app.main:app --host 0.0.0.0 --port 9001 --reload
