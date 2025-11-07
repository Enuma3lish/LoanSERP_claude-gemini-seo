#!/bin/bash
# Diagnostic script for empty "Top 5 關鍵字曝光比較" chart issue

echo "========================================"
echo "LoanSERP Chart Debugging Tool"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Step 1: Check if Docker services are running
echo "Step 1: Checking Docker services..."
docker ps | grep -q postgres
POSTGRES_RUNNING=$?
print_status $POSTGRES_RUNNING "PostgreSQL container"

docker ps | grep -q redis
REDIS_RUNNING=$?
print_status $REDIS_RUNNING "Redis container"
echo ""

# Step 2: Check if backend is running
echo "Step 2: Checking Backend services..."
curl -s http://localhost:8000/api/health > /dev/null 2>&1
BACKEND_RUNNING=$?
print_status $BACKEND_RUNNING "Django backend (port 8000)"

curl -s http://localhost:9001/health > /dev/null 2>&1
LLM_RUNNING=$?
print_status $LLM_RUNNING "LLM Broker (port 9001)"
echo ""

# Step 3: Check database data
echo "Step 3: Checking database for exposure data..."
if [ -f backend/manage.py ]; then
    cd backend

    # Activate virtual environment if it exists
    if [ -d "../venv" ]; then
        source ../venv/bin/activate 2>/dev/null || source ../venv/Scripts/activate 2>/dev/null
    fi

    # Check keyword count
    KEYWORD_COUNT=$(python manage.py shell -c "from exposure.models import Keyword; print(Keyword.objects.count())" 2>/dev/null)
    if [ ! -z "$KEYWORD_COUNT" ]; then
        if [ "$KEYWORD_COUNT" -gt 0 ]; then
            print_status 0 "Found $KEYWORD_COUNT keywords in database"
        else
            print_status 1 "No keywords found in database"
        fi
    fi

    # Check exposure snapshot count
    SNAPSHOT_COUNT=$(python manage.py shell -c "from exposure.models import ExposureSnapshot; print(ExposureSnapshot.objects.count())" 2>/dev/null)
    if [ ! -z "$SNAPSHOT_COUNT" ]; then
        if [ "$SNAPSHOT_COUNT" -gt 0 ]; then
            print_status 0 "Found $SNAPSHOT_COUNT exposure snapshots in database"
        else
            print_status 1 "No exposure snapshots found in database"
        fi
    fi

    cd ..
else
    print_warning "Could not find backend/manage.py"
fi
echo ""

# Step 4: Test API endpoint
echo "Step 4: Testing API endpoint..."
if [ $BACKEND_RUNNING -eq 0 ]; then
    END_DATE=$(date +%Y-%m-%d)
    START_DATE=$(date -d "7 days ago" +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d 2>/dev/null)

    API_URL="http://localhost:8000/api/exposure/top5_timeseries_auto?start=$START_DATE&end=$END_DATE&pull=false"
    echo "Testing: $API_URL"

    RESPONSE=$(curl -s "$API_URL")
    echo "Response preview:"
    echo "$RESPONSE" | head -c 200
    echo "..."
    echo ""

    # Check if response contains series
    echo "$RESPONSE" | grep -q '"series"'
    HAS_SERIES=$?
    print_status $HAS_SERIES "API response contains 'series' field"

    # Check if series is not empty
    SERIES_COUNT=$(echo "$RESPONSE" | grep -o '"series":\[\]' | wc -l)
    if [ "$SERIES_COUNT" -gt 0 ]; then
        print_status 1 "Series array is empty"
    else
        print_status 0 "Series array has data"
    fi
else
    print_warning "Backend is not running, skipping API test"
fi
echo ""

# Summary and recommendations
echo "========================================"
echo "Summary & Recommendations"
echo "========================================"
echo ""

if [ $POSTGRES_RUNNING -ne 0 ] || [ $REDIS_RUNNING -ne 0 ]; then
    echo "1. Start Docker services:"
    echo "   cd docker && docker-compose up -d"
    echo ""
fi

if [ $BACKEND_RUNNING -ne 0 ]; then
    echo "2. Start the backend services:"
    echo "   ./start-all.sh"
    echo ""
fi

if [ "$SNAPSHOT_COUNT" == "0" ] || [ -z "$SNAPSHOT_COUNT" ]; then
    echo "3. Database appears to be empty. Create test data:"
    echo "   cd backend"
    echo "   python create_test_data.py 30"
    echo ""
    echo "   Or pull real data from Google Search Console:"
    echo "   python manage.py pull_gsc_data --start=2024-10-01 --end=2024-10-31"
    echo ""
fi

echo "4. Open browser console (F12) and check for errors:"
echo "   - Network tab: Look for failed API requests"
echo "   - Console tab: Look for the debug logs we added"
echo ""

echo "5. After fixing, refresh the frontend and try again"
echo ""
