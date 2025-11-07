# Debugging Empty "Top 5 關鍵字曝光比較" Chart

## Problem Description
The "Top 5 關鍵字曝光比較" (Top 5 Keyword Exposure Comparison) chart in the frontend dashboard is empty/not displaying.

## Quick Diagnosis
Run the diagnostic script to identify the issue:
```bash
./diagnose-empty-chart.sh
```

## Common Causes & Solutions

### 1. Database is Empty (Most Likely)
**Symptom:** API returns empty series array `{"series": [], "keywords": [], "dates": []}`

**Solution A - Create Test Data:**
```bash
cd backend
# Activate virtual environment if you have one
source ../venv/bin/activate  # Linux/Mac
# or
source ../venv/Scripts/activate  # Windows

# Create 30 days of test data
python create_test_data.py 30
```

**Solution B - Pull Real Data from Google Search Console:**
```bash
cd backend
# Make sure GSC credentials are configured
python manage.py pull_gsc_data --start=2024-10-01 --end=2024-11-07
```

### 2. Backend Services Not Running
**Symptom:** Network errors in browser console, failed to connect to localhost:8000

**Solution:**
```bash
# Start all backend services
./start-all.sh

# Or start individually:
./start-backend.sh      # Django on port 8000
./start-llm-broker.sh   # FastAPI on port 9001
```

### 3. Docker Services Not Running
**Symptom:** Backend fails to start, database connection errors

**Solution:**
```bash
cd docker
docker-compose up -d
# Wait a few seconds for containers to start
docker-compose ps  # Verify all containers are running
```

### 4. CORS Issues
**Symptom:** Browser console shows CORS errors

**Check:** Backend should have django-cors-headers installed and configured.

**Verify:**
```bash
cd backend
pip install -r requirements-cors.txt
```

The backend `loanserp/base.py` should have:
```python
INSTALLED_APPS = [
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ...
]

CORS_ALLOW_ALL_ORIGINS = True  # For development only
```

### 5. Frontend Not Updated
**Symptom:** Old code is running

**Solution:**
```bash
cd frontend
# Clear cache and rebuild
rm -rf node_modules/.cache
ng serve --host 0.0.0.0
```

## Using the Debug Logs

I've added comprehensive debugging logs to the frontend code. To use them:

1. Open your browser to `http://localhost:4200`
2. Open Developer Tools (F12)
3. Go to the Console tab
4. Select a date range in the dashboard
5. Watch for these debug messages:

### Expected Log Flow (When Working):
```
Fetching data for date range: 2024-10-01 to 2024-10-31
Received response from backend: {period: {...}, keywords: [...], dates: [...], series: [...]}
Response series: [{name: "貸款", data: [...]}, ...]
Response keywords: ["貸款", "房屋貸款", ...]
Response dates: ["2024-10-01", "2024-10-02", ...]
updateChartData called with response: {...}
Set charts[0].data to: [{name: "貸款", data: [...]}, ...]
Set charts[1].data (貸款) to: [1234, 1456, ...]
...
ChartCard updateChart called for: Top 5 關鍵字曝光比較
  chartData: [{name: "貸款", data: [...]}, ...]
  dates: ["2024-10-01", ...]
ChartCard chart option created for: Top 5 關鍵字曝光比較
  Number of series: 5
  Series: [{name: "貸款", type: "line", ...}, ...]
```

### Problem Indicators:

#### Empty Database:
```
Received response from backend: {period: {...}, keywords: [], dates: [], series: []}
No series data received from backend
後端返回的資料為空，請檢查資料庫是否有資料
```

#### Backend Not Running:
```
Backend API error: HttpErrorResponse {status: 0, ...}
Error message: Http failure response for http://localhost:8000/api/...: 0 Unknown Error
```

#### CORS Error:
```
Access to XMLHttpRequest at 'http://localhost:8000/api/...' from origin 'http://localhost:4200'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present...
```

#### Invalid Data Format:
```
ChartCard updateChart early return - missing data
  chartData is null/undefined: true
```

## Step-by-Step Troubleshooting

1. **Check all services are running:**
   ```bash
   # Check Docker
   docker ps
   # Should see postgres and redis containers

   # Check backend
   curl http://localhost:8000/api/health
   # Should return: {"ok": true}

   # Check LLM broker
   curl http://localhost:9001/health
   # Should return health status
   ```

2. **Check database has data:**
   ```bash
   cd backend
   python manage.py shell
   ```
   ```python
   from exposure.models import Keyword, ExposureSnapshot
   print(f"Keywords: {Keyword.objects.count()}")
   print(f"Snapshots: {ExposureSnapshot.objects.count()}")
   # Should show non-zero numbers
   ```

3. **Test the API directly:**
   ```bash
   # Test with curl
   curl "http://localhost:8000/api/exposure/top5_timeseries_auto?start=2024-10-01&end=2024-10-31&pull=false"
   ```

   Should return something like:
   ```json
   {
     "period": {"start": "2024-10-01", "end": "2024-10-31", "days": 31},
     "keywords": ["貸款", "房屋貸款", "個人信貸", "車貸", "信用貸款"],
     "dates": ["2024-10-01", "2024-10-02", ...],
     "series": [
       {"name": "貸款", "data": [1234, 1456, ...]},
       ...
     ]
   }
   ```

4. **Check browser console for specific errors**
   - Open DevTools (F12)
   - Go to Console tab
   - Look for error messages
   - Go to Network tab
   - Filter by "top5_timeseries"
   - Check the response

5. **Verify frontend is making the request**
   - In Network tab, you should see a request to:
     `http://localhost:8000/api/exposure/top5_timeseries_auto?start=...&end=...&pull=true`
   - Click on it to see the response

## After Fixing

Once you've identified and fixed the issue:

1. **Remove debug logs** (optional, they can stay for now):
   The debug logs are helpful and don't hurt performance, but if you want to remove them,
   I can do that in a follow-up commit.

2. **Test the fix:**
   - Refresh the frontend (`Ctrl+R` or `Cmd+R`)
   - Select a date range (7-90 days)
   - Click "分析趨勢"
   - Charts should appear with data

3. **Verify all 6 charts load:**
   - Chart 1: Comparison chart with all 5 keywords
   - Charts 2-6: Individual keyword trend analysis

## Still Having Issues?

If you're still experiencing problems after following these steps:

1. Share the browser console output
2. Share the output of `./diagnose-empty-chart.sh`
3. Share any error messages from the backend terminal
4. Share the API response from the curl test

## Quick Fix Summary

For most cases (empty database), this should fix it:

```bash
# 1. Make sure Docker is running
cd docker && docker-compose up -d

# 2. Start backend services
cd ..
./start-all.sh

# 3. Create test data (in a new terminal)
cd backend
python create_test_data.py 30

# 4. Refresh frontend
# Go to http://localhost:4200 and select a date range
```
