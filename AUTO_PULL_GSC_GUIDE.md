# Google Search Console Auto-Pull Feature

## Overview

The auto-pull feature automatically fetches data from Google Search Console when users select a date range that has missing data in the database.

## How It Works

### Previous Behavior (Test Data Only)
```
User selects dates → Frontend → Backend → Database
                                    ↓
                            Returns existing data only
                            (empty if no data)
```

### New Behavior (Auto-Pull)
```
User selects dates → Frontend → Backend
                                    ↓
                            Check database for data
                                    ↓
                    ┌───────────────┴────────────────┐
                    ↓                                ↓
            Data exists?                      Data missing?
                    ↓                                ↓
            Return data                   Pull from GSC API
                                                    ↓
                                            Save to database
                                                    ↓
                                            Return fresh data
```

## Setup Requirements

### 1. Google Search Console API Credentials

You need to authenticate with Google Search Console first:

```bash
cd backend
source .venv/bin/activate

# Step 1: Place your OAuth credentials
# Download from: https://console.cloud.google.com/apis/credentials
# Save as: backend/credentials/client_secret.json

# Step 2: Authenticate (one-time setup)
python manage.py gsc_auth

# This will:
# - Open browser for Google OAuth
# - Save token to: backend/credentials/token.json
```

### 2. Configure GSC Settings

In `backend/loanserp/base.py`:

```python
# GSC Property URI (your website)
GSC_PROPERTY_URI = os.getenv("GSC_PROPERTY_URI", "sc-domain:your-domain.com")

# Keywords to track
KEYWORD_TRACK_LIST = [
    "貸款",
    "房屋貸款",
    "個人信貸",
    "車貸",
    "信用貸款"
]

# OAuth files
GSC_CLIENT_SECRETS_FILE = os.getenv(
    "GSC_CLIENT_SECRETS_FILE",
    str(BASE_DIR / "credentials" / "client_secret.json")
)
GSC_TOKEN_FILE = os.getenv(
    "GSC_TOKEN_FILE",
    str(BASE_DIR / "credentials" / "token.json")
)
```

## API Endpoints

### New Endpoint: `/api/exposure/top5_timeseries_auto`

**Automatically pulls from GSC if data is missing**

```bash
GET /api/exposure/top5_timeseries_auto?start=2025-10-01&end=2025-10-14&pull=true

Query Parameters:
- start: Start date (YYYY-MM-DD)
- end: End date (YYYY-MM-DD)
- pull: Enable auto-pull (default: 'true')
  - 'true', '1', 'yes' → Enable
  - 'false', '0', 'no' → Disable

Response:
{
  "period": {
    "start": "2025-10-01",
    "end": "2025-10-14",
    "days": 14
  },
  "keywords": ["貸款", "房屋貸款", ...],
  "dates": ["2025-10-01", "2025-10-02", ...],
  "series": [
    {"name": "貸款", "data": [1234, 1456, ...]},
    ...
  ],
  "pull_status": {
    "had_data": false,
    "pulled": true,
    "pull_result": {
      "success": true,
      "keywords_pulled": 5,
      "snapshots_created": 70,
      "date_range": "2025-10-01 to 2025-10-14",
      "errors": []
    },
    "missing_dates_count": 14
  }
}
```

### Existing Endpoint: `/api/exposure/top5_timeseries`

**No auto-pull, returns only existing database data**

```bash
GET /api/exposure/top5_timeseries?start=2025-10-01&end=2025-10-14

Response:
{
  "period": {...},
  "keywords": [...],
  "dates": [...],
  "series": [...]
  // No pull_status
}
```

## Frontend Integration

The frontend now uses auto-pull by default:

**File:** `frontend/src/app/components/dashboard/dashboard.component.ts`

```typescript
// Old way (database only)
this.backendApi.getTop5Timeseries(startStr, endStr).subscribe(...)

// New way (auto-pull enabled)
this.backendApi.getTop5TimeseriesAuto(startStr, endStr, true).subscribe(...)
```

### User Experience

1. User selects date range (e.g., 7 days)
2. User clicks "分析趨勢"
3. **If data exists:** Charts load immediately
4. **If data missing:**
   - Backend pulls from GSC (takes 2-5 seconds)
   - Data saved to database
   - Charts load with fresh data
5. Future requests for same dates load instantly (from database)

## Testing

### Test Auto-Pull

```bash
# 1. Clear database (optional - to force pull)
cd backend
source .venv/bin/activate
python manage.py shell -c "from exposure.models import ExposureSnapshot; ExposureSnapshot.objects.all().delete(); print('Data cleared')"

# 2. Make request with dates that have no data
curl "http://localhost:8000/api/exposure/top5_timeseries_auto?start=2025-09-01&end=2025-09-07"

# Should see:
# "pull_status": {
#   "had_data": false,
#   "pulled": true,
#   "pull_result": {
#     "success": true,
#     "keywords_pulled": 5,
#     "snapshots_created": 35
#   }
# }

# 3. Make same request again
curl "http://localhost:8000/api/exposure/top5_timeseries_auto?start=2025-09-01&end=2025-09-07"

# Should see:
# "pull_status": {
#   "had_data": true,
#   "pulled": false
# }
```

### Test Frontend

1. Open http://localhost:4200
2. Select future dates (not in test data): e.g., tomorrow to 7 days from now
3. Click "分析趨勢"
4. Backend will pull from GSC
5. Charts will display with real GSC data!

## Performance Considerations

### Caching Strategy

The system uses a smart caching approach:

1. **First request:** Pulls from GSC (2-5 seconds)
2. **Subsequent requests:** Instant (from database)
3. **Partial data:** Only pulls missing dates

### Rate Limits

Google Search Console API has rate limits:
- **Requests per day:** 1,200
- **Requests per 100 seconds:** 100

**Recommendation:**
- Use test data for development
- Only enable auto-pull in production
- Consider implementing request throttling

### Database Storage

Each snapshot takes ~100 bytes:
- 5 keywords × 90 days = 450 snapshots = ~45KB
- 1 year of data = ~180KB
- Very efficient storage

## Configuration Options

### Disable Auto-Pull (Use Manual Data Only)

**Option 1: Frontend Toggle**

```typescript
// In dashboard.component.ts
this.backendApi.getTop5TimeseriesAuto(startStr, endStr, false) // Auto-pull disabled
```

**Option 2: Use Original Endpoint**

```typescript
// In dashboard.component.ts
this.backendApi.getTop5Timeseries(startStr, endStr) // No auto-pull, database only
```

**Option 3: Query Parameter**

```bash
curl "http://localhost:8000/api/exposure/top5_timeseries_auto?start=2025-09-01&end=2025-09-07&pull=false"
```

### Customize Keywords

Edit `backend/loanserp/base.py`:

```python
KEYWORD_TRACK_LIST = [
    "your keyword 1",
    "your keyword 2",
    "your keyword 3",
]
```

Or set environment variable:

```bash
export KEYWORD_TRACK_LIST="keyword1,keyword2,keyword3"
```

## Troubleshooting

### Issue: "GSC authentication failed"

**Solution:**

```bash
cd backend
source .venv/bin/activate

# Re-authenticate
python manage.py gsc_auth

# Check credentials file exists
ls -la credentials/
# Should show: client_secret.json, token.json
```

### Issue: "No data returned from GSC"

**Possible causes:**

1. **Date range too recent:** GSC data has 2-3 day delay
   ```bash
   # Try older dates
   curl "http://localhost:8000/api/exposure/top5_timeseries_auto?start=2025-10-01&end=2025-10-07"
   ```

2. **Wrong property URI:** Check your domain
   ```python
   # In base.py
   GSC_PROPERTY_URI = "sc-domain:your-actual-domain.com"
   ```

3. **No impressions for keywords:** Keywords may not have any traffic
   ```bash
   # Check GSC directly: https://search.google.com/search-console
   ```

### Issue: "Auto-pull is slow"

This is normal for first request:
- GSC API takes 2-5 seconds
- Subsequent requests are instant
- Consider showing loading message: "Fetching fresh data from Google..."

### Issue: "Rate limit exceeded"

```json
{
  "pull_status": {
    "errors": ["Rate limit exceeded"]
  }
}
```

**Solution:** Wait a few minutes and try again, or use existing data:

```bash
# Use database-only endpoint
curl "http://localhost:8000/api/exposure/top5_timeseries?start=2025-10-01&end=2025-10-07"
```

## Advanced Usage

### Manual Pull for Specific Dates

```bash
cd backend
source .venv/bin/activate
python manage.py gsc_pull --days=30
```

### Check Data Coverage

```bash
cd backend
source .venv/bin/activate
python -c "
import django
django.setup()
from exposure.gsc_auto_pull import check_data_coverage
from datetime import date

start = date(2025, 10, 1)
end = date(2025, 10, 14)
keywords = ['貸款', '房屋貸款']

has_data, missing = check_data_coverage(start, end, keywords)
print(f'Has complete data: {has_data}')
print(f'Missing dates: {missing}')
"
```

### Programmatic Pull

```python
from exposure.gsc_auto_pull import pull_gsc_data_for_range
from datetime import date

start = date(2025, 10, 1)
end = date(2025, 10, 14)
keywords = ['貸款', '房屋貸款', '個人信貸']

result = pull_gsc_data_for_range(start, end, keywords)
print(result)
```

## Files Created

1. **`backend/exposure/gsc_auto_pull.py`** - Auto-pull logic
2. **`backend/exposure/views.py`** - New endpoint added
3. **`backend/loanserp/urls.py`** - Route registered
4. **`frontend/src/app/services/backend-api.service.ts`** - New method
5. **`frontend/src/app/components/dashboard/dashboard.component.ts`** - Using auto-pull
6. **`AUTO_PULL_GSC_GUIDE.md`** - This guide

## Summary

**Before:**
- ❌ Had to manually run `python manage.py gsc_pull`
- ❌ Frontend showed empty charts if data missing
- ❌ Required pre-populating database

**After:**
- ✅ Automatic data pull when user selects dates
- ✅ Seamless user experience
- ✅ Smart caching (pull once, use many times)
- ✅ Graceful fallback if GSC unavailable

**Next Steps:**
1. Setup GSC authentication (one-time)
2. Restart backend
3. Try selecting new date ranges in frontend
4. Watch auto-pull in action!

---

**Created by:** Melo Wu
**Date:** 2025-11-04
**Feature:** Google Search Console Auto-Pull
