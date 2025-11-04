# LoanSERP Troubleshooting Guide

## Quick Diagnosis

Run these commands to check system status:

```bash
# 1. Check Django Backend
curl http://localhost:8000/api/health
# Expected: {"ok":true}

# 2. Check LLM Broker
curl http://localhost:9001/v1/health
# Expected: {"ok":true,...}

# 3. Check if data exists
cd backend
source .venv/bin/activate
python manage.py shell -c "from exposure.models import ExposureSnapshot; print(f'Snapshots: {ExposureSnapshot.objects.count()}')"
# Expected: Snapshots: > 0

# 4. Check Frontend
# Open http://localhost:4200 in browser
```

---

## Common Issues & Solutions

### Issue 1: "無法載入資料，請確認後端服務是否正常運行"

**English:** "Unable to load data, please confirm backend service is running"

**Possible Causes:**

#### A. Backend not running
```bash
curl http://localhost:8000/api/health
# If this fails, start the backend:
cd backend
./START_BACKEND.sh
```

#### B. No data in database ⭐ **MOST COMMON**
```bash
# Check if data exists
cd backend
source .venv/bin/activate
python -c "import django; django.setup(); from exposure.models import ExposureSnapshot; print(ExposureSnapshot.objects.count())"

# If count is 0, create test data:
python create_test_data.py 30
```

#### C. CORS not configured
```bash
# Install CORS headers
cd backend
source .venv/bin/activate
pip install django-cors-headers

# Restart backend
./START_BACKEND.sh
```

#### D. Wrong date range
- Frontend requires at least 7 days of data
- Make sure your date range has data in the database
- Test data is created for the last 30 days from today

---

### Issue 2: LLM Explanations Show "正在生成趨勢分析..." Forever

**Cause:** LLM broker health shows `"gemini":false,"claude":false`

**Solution:** Set API keys

```bash
# Option 1: Export environment variables
export GEMINI_API_KEY="your-gemini-api-key"
export CLAUDE_API_KEY="your-claude-api-key"

# Option 2: Create .env file in geo_LLM_infra/llm_broker/
cd geo_LLM_infra/llm_broker
cat > .env << EOF
GEMINI_API_KEY=your-gemini-api-key-here
CLAUDE_API_KEY=your-claude-api-key-here
REDIS_URL=redis://localhost:6379/0
EOF

# Restart LLM broker
./START_LLM_BROKER.sh
```

**Note:** Charts will still work without LLM, but explanations won't generate.

---

### Issue 3: LLM Broker Shows "cache":false

**Cause:** Redis not running

**Solution:**

```bash
# Check if Redis is running
redis-cli ping
# Expected: PONG

# If not running, start Redis:
redis-server

# Or on Ubuntu/Debian:
sudo systemctl start redis

# Or on macOS:
brew services start redis
```

**Note:** Cache is optional. LLM will work without Redis, just slower.

---

### Issue 4: CORS Errors in Browser Console

**Error:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/...' from origin 'http://localhost:4200'
has been blocked by CORS policy
```

**Solution:**

```bash
cd backend
source .venv/bin/activate

# Install django-cors-headers
pip install django-cors-headers

# Verify CORS is in settings
python manage.py shell -c "from django.conf import settings; print('corsheaders' in settings.INSTALLED_APPS)"
# Should print: True

# Restart backend
./START_BACKEND.sh
```

---

### Issue 5: Charts Show Empty/Blank

**Causes & Solutions:**

#### A. No data for selected date range
```bash
# Check what dates have data
cd backend
source .venv/bin/activate
python manage.py shell -c "from exposure.models import ExposureSnapshot; from django.db.models import Min, Max; dates = ExposureSnapshot.objects.aggregate(Min('date'), Max('date')); print(f\"Data from {dates['date__min']} to {dates['date__max']}\")"
```

#### B. Date range too short
- Minimum 7 days required
- Check date picker validation

#### C. Keywords have no impressions
```bash
# Check data
cd backend
source .venv/bin/activate
python manage.py shell -c "from exposure.models import ExposureSnapshot; print(ExposureSnapshot.objects.values('keyword__name').distinct())"
```

---

### Issue 6: Frontend Shows Build Errors

**Error:** `Module not found` or Angular compilation errors

**Solution:**

```bash
cd frontend

# Clean install
rm -rf node_modules package-lock.json
npm install

# If still failing, check Node.js version
node -v
# Should be 18+

# Update Angular CLI if needed
npm install -g @angular/cli@18
```

---

### Issue 7: Database Connection Error

**Error:** `django.db.utils.OperationalError: could not connect to server`

**Solution:**

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql
# Or on macOS:
brew services list

# Start PostgreSQL
sudo systemctl start postgresql
# Or on macOS:
brew services start postgresql

# Test connection
psql -U loan -d loanserp -h localhost
```

---

## Testing Each Component

### Test Backend

```bash
# Health check
curl http://localhost:8000/api/health

# Get data
curl "http://localhost:8000/api/exposure/top5_timeseries?start=2025-10-20&end=2025-10-27"

# Should return JSON with keywords and data
```

### Test LLM Broker

```bash
# Health check
curl http://localhost:9001/v1/health

# Test analysis (requires data from backend first)
curl -X POST http://localhost:9001/v1/summarize/trend \
  -H "Content-Type: application/json" \
  -d '{
    "period": {"start": "2025-10-20", "end": "2025-10-27", "days": 8},
    "top_keywords": ["貸款"],
    "dates": ["2025-10-20", "2025-10-21"],
    "series": [{"name": "貸款", "data": [1000, 1100]}],
    "use_cache": false
  }'
```

### Test Frontend

1. Open http://localhost:4200
2. Check browser console (F12) for errors
3. Try selecting last 7 days
4. Click "分析趨勢"

---

## Data Management

### Create Test Data

```bash
cd backend
source .venv/bin/activate

# Create 30 days of test data
python create_test_data.py 30

# Create 60 days of test data
python create_test_data.py 60

# Create 90 days of test data (maximum for frontend)
python create_test_data.py 90
```

### Clear All Data

```bash
cd backend
source .venv/bin/activate

python manage.py shell -c "from exposure.models import ExposureSnapshot, Keyword; ExposureSnapshot.objects.all().delete(); Keyword.objects.all().delete(); print('All data deleted')"
```

### Import Real GSC Data

```bash
cd backend
source .venv/bin/activate

# Authenticate with Google
python manage.py gsc_auth

# Pull data for last 30 days
python manage.py gsc_pull --days=30
```

---

## Environment Check

Run this comprehensive check:

```bash
#!/bin/bash

echo "=== LoanSERP System Check ==="
echo ""

# 1. Backend
echo "1. Backend (Django):"
curl -s http://localhost:8000/api/health && echo " ✓" || echo " ✗ NOT RUNNING"

# 2. LLM Broker
echo "2. LLM Broker:"
curl -s http://localhost:9001/v1/health && echo " ✓" || echo " ✗ NOT RUNNING"

# 3. Frontend
echo "3. Frontend:"
curl -s http://localhost:4200 > /dev/null && echo " ✓" || echo " ✗ NOT RUNNING"

# 4. Database
echo "4. Database:"
cd backend
source .venv/bin/activate
python -c "import django; django.setup(); from exposure.models import ExposureSnapshot; count = ExposureSnapshot.objects.count(); print(f'  Snapshots: {count}')"

# 5. Redis
echo "5. Redis:"
redis-cli ping > /dev/null 2>&1 && echo " ✓ RUNNING" || echo " ✗ NOT RUNNING (optional)"

echo ""
echo "=== End Check ==="
```

---

## Quick Fix for Common Scenario

**Scenario:** Fresh setup, nothing works

```bash
# 1. Start PostgreSQL
sudo systemctl start postgresql

# 2. Start Redis (optional)
sudo systemctl start redis

# 3. Backend setup
cd backend
source .venv/bin/activate
pip install -r requirements.txt
pip install django-cors-headers
python manage.py migrate
python create_test_data.py 30
./START_BACKEND.sh

# In new terminal - 4. LLM Broker
cd geo_LLM_infra/llm_broker
source .venv/bin/activate
pip install -r requirements.txt
./START_LLM_BROKER.sh

# In new terminal - 5. Frontend
cd frontend
npm install
npm start
```

Then open: http://localhost:4200

---

## Getting Help

### Check Logs

**Backend:**
- Django prints to terminal where you ran `./START_BACKEND.sh`
- Look for errors in red

**LLM Broker:**
- Uvicorn prints to terminal where you ran `./START_LLM_BROKER.sh`
- Look for 500 errors or exceptions

**Frontend:**
- Open browser console (F12 → Console tab)
- Look for red errors
- Check Network tab for failed requests

### Debug Mode

Enable verbose logging:

**Django:**
```python
# In backend/loanserp/base.py
DEBUG = True  # Should already be True in development
```

**Frontend:**
```typescript
// In frontend/src/app/services/*.service.ts
// Add console.log() to see requests/responses
```

---

**Last Updated:** 2025-11-04
