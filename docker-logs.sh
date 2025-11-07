#!/bin/bash
# =============================================================================
# LoanSERP Docker Logs Viewer
# =============================================================================

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================"
echo "  LoanSERP Logs Viewer"
echo -e "========================================${NC}"
echo ""

if [ -z "$1" ]; then
    echo "Available services:"
    echo "  - frontend"
    echo "  - backend"
    echo "  - celery-worker"
    echo "  - celery-beat"
    echo "  - llm-broker"
    echo "  - postgres"
    echo "  - redis"
    echo ""
    echo "Usage examples:"
    echo "  ./docker-logs.sh backend          # View backend logs"
    echo "  ./docker-logs.sh                  # View all logs"
    echo "  ./docker-logs.sh backend -f       # Follow backend logs"
    echo ""
    echo -e "${GREEN}Showing all service logs (press Ctrl+C to exit):${NC}"
    echo ""
    docker compose logs -f --tail=100
else
    SERVICE=$1
    shift  # Remove first argument
    echo -e "${GREEN}Showing logs for: $SERVICE${NC}"
    echo ""
    docker compose logs "$@" --tail=100 $SERVICE
fi
