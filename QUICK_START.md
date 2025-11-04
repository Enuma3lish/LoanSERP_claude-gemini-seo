# LoanSERP Quick Start Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Setup Backend with Test Data

```bash
cd backend
# Activate your venv
source .venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt
pip install django-cors-headers

# Create test data (30 days of sample data)
python create_test_data.py 30
```

### Step 2: Start Backend Services

**Terminal 1 - Django Backend:**
```bash
cd backend
# Option 1: Use the automated script
./START_BACKEND.sh

# Option 2: Manual start
source .venv/bin/activate
python manage.py runserver
```

**Terminal 2 - LLM Broker:**
```bash
cd geo_LLM_infra/llm_broker

# Option 1: Use the automated script (recommended)
./START_LLM_BROKER.sh

# Option 2: Manual start
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 9001 --reload
```

### Step 3: Start Frontend

**Terminal 3 - Angular:**
```bash
cd frontend
npm install
npm start
```

Then open: **http://localhost:4200**

---

## ✅ Fixed Issues

### Issue: `ModuleNotFoundError: No module named 'exposure.crawler'`

**Status**: ✅ FIXED

**What was done**:
- Commented out the crawler import in `backend/exposure/views.py:8`
- Commented out two unused views (`crawl_top5_news_csv` and `crawl_top5_news_json`)
- These views are not needed for the frontend functionality

**Files affected**:
- `backend/exposure/views.py` - Lines 8, 173-283

The frontend only uses:
- ✓ `/api/health`
- ✓ `/api/exposure/top5_timeseries`
- ✓ `/api/exposure/top5_compare`

All of these endpoints work correctly now.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL running (for Django)
- [ ] Redis running (for LLM caching)
- [ ] Environment variables set:
  - [ ] `GEMINI_API_KEY`
  - [ ] `CLAUDE_API_KEY`
  - [ ] Database credentials

---

## 🔍 Verify Everything Works

### 1. Check Backend
```bash
curl http://localhost:8000/api/health
# Expected: {"ok":true}
```

### 2. Check LLM Broker
```bash
curl http://localhost:9001/v1/health
# Expected: {"ok":true,"service":"LoanSERP LLM Broker",...}
```

### 3. Check Frontend
Open browser to: `http://localhost:4200`

You should see:
- Date range picker
- Empty state message
- No console errors

### 4. Test End-to-End
1. Select date range (e.g., last 7 days)
2. Click "分析趨勢"
3. Watch charts load
4. See AI explanations appear

---

## 🐛 Common Issues

### Issue: "No data in charts"

**Cause**: No GSC data in database

**Solution**:
```bash
cd backend
python manage.py gsc_pull --days=30
```

### Issue: "CORS error"

**Cause**: CORS headers not installed

**Solution**:
```bash
pip install django-cors-headers
# Then restart Django server
```

### Issue: "LLM service unavailable"

**Cause**: Missing API keys or Redis not running

**Solution**:
1. Check `.env` file has `GEMINI_API_KEY` and `CLAUDE_API_KEY`
2. Start Redis: `redis-server`
3. Restart LLM broker

---

## 📁 Project Structure

```
LoanSERP_claude-gemini-seo/
├── backend/              # Django (port 8000)
├── geo_LLM_infra/       # LLM Broker (port 9001)
└── frontend/            # Angular (port 4200)
```

---

## 🎯 What You Get

1. **Interactive Dashboard** with 6 charts
2. **Date Range Validation** (7-90 days)
3. **AI-Powered Analysis** (Gemini + Claude)
4. **Real-time Updates**
5. **Responsive Design**

---

## 📚 Full Documentation

- **Setup Guide**: See `SETUP_GUIDE.md`
- **Implementation Details**: See `FRONTEND_IMPLEMENTATION_SUMMARY.md`
- **Frontend Docs**: See `frontend/README.md`

---

## 🆘 Need Help?

1. Check console for errors (F12 in browser)
2. Verify all 3 services are running
3. Check network tab in browser DevTools
4. Review log output from Django and LLM broker

---

**Ready to go!** 🎉

Start with Terminal 1 (Django), then Terminal 2 (LLM), then Terminal 3 (Angular).
