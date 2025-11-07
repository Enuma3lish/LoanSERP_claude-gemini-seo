#!/bin/bash
# =============================================================================
# LoanSERP Docker Stop Script
# =============================================================================

set -e

echo "========================================"
echo "  Stopping LoanSERP Services"
echo "========================================"
echo ""

# Check if user wants to remove volumes
if [ "$1" == "--clean" ] || [ "$1" == "-c" ]; then
    echo "⚠️  Stopping services and removing volumes (data will be lost)..."
    echo "   Press Ctrl+C within 5 seconds to cancel..."
    sleep 5
    docker compose down -v
    echo ""
    echo "✅ Services stopped and volumes removed"
    echo "   All data has been deleted"
else
    docker compose down
    echo ""
    echo "✅ Services stopped"
    echo "   Data preserved in ./data directory"
    echo ""
    echo "To remove all data, run: ./docker-stop.sh --clean"
fi

echo ""
