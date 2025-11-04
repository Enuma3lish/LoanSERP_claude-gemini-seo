# LoanSERP Analytics Platform - Setup Guide

## Overview

This guide will help you set up the complete LoanSERP Analytics platform, which consists of:

1. **Django Backend** (port 8000) - Serves GSC data and top 5 keywords analysis
2. **LLM Broker** (port 9001) - FastAPI service for AI-powered trend analysis
3. **Angular Frontend** (port 4200) - Interactive dashboard with charts

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Angular 18 Frontend                       │
│                   (http://localhost:4200)                    │
│                                                              │
│  • Date Range Picker (7-90 days validation)                 │
│  • 6 Interactive Charts (ECharts)                            │
│  • Synchronous LLM Explanations                             │
└──────────────┬────────────────────────────┬─────────────────┘
               │                            │
               │                            │
      ┌────────▼─────────┐         ┌────────▼──────────┐
      │  Django Backend  │         │   LLM Broker      │
      │  (port 8000)     │         │   (port 9001)     │
      │                  │         │                   │
      │  • GSC Data      │         │  • Gemini API     │
      │  • Top 5 KWs     │         │  • Claude API     │
      │  • PostgreSQL    │         │  • Redis Cache    │
      └──────────────────┘         └───────────────────┘
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- API Keys:
  - Google Gemini API Key
  - Anthropic Claude API Key
  - Google Search Console credentials

## Step 1: Backend Setup (Django)

### 1.1 Install Dependencies

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-cors.txt
```

### 1.2 Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=true
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
POSTGRES_DB=loanserp
POSTGRES_USER=loan
POSTGRES_PASSWORD=loanpwd
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1

# GSC
GSC_PROPERTY_URI=sc-domain:your-domain.com
```

### 1.3 Initialize Database

```bash
# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 1.4 Start Django Server

```bash
python manage.py runserver 0.0.0.0:8000
```

Verify: `http://localhost:8000/api/health`

## Step 2: LLM Broker Setup (FastAPI)

### 2.1 Navigate to LLM Broker

```bash
cd geo_LLM_infra/llm_broker
```

### 2.2 Install Dependencies

```bash
pip install fastapi uvicorn anthropic google-generativeai redis
```

### 2.3 Configure Environment Variables

Create a `.env` file:

```bash
# LLM Broker
LLM_BROKER_HOST=0.0.0.0
LLM_BROKER_PORT=9001

# Redis Cache
REDIS_URL=redis://localhost:6379/0
LLM_CACHE_TTL_SEC=259200

# LLM API Keys
GEMINI_API_KEY=your-gemini-api-key-here
CLAUDE_API_KEY=your-claude-api-key-here

# Models
PREFERRED_MODELS=gemini-2.0-flash,claude-3-5-sonnet-20241022

# Output
OUTPUT_LANG=zh-tw
```

### 2.4 Start LLM Broker

```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

Verify: `http://localhost:9001/v1/health`

## Step 3: Frontend Setup (Angular 18)

### 3.1 Navigate to Frontend

```bash
cd frontend
```

### 3.2 Install Dependencies

```bash
npm install
```

### 3.3 Start Development Server

```bash
npm start
```

The app will be available at: `http://localhost:4200`

## Step 4: Verification

### 4.1 Check All Services

1. **Backend**: `curl http://localhost:8000/api/health`
   - Should return: `{"ok": true}`

2. **LLM Broker**: `curl http://localhost:9001/v1/health`
   - Should return health status with provider info

3. **Frontend**: Open `http://localhost:4200` in browser
   - Should see the dashboard

### 4.2 Test End-to-End Flow

1. Open `http://localhost:4200`
2. Select a date range (e.g., last 7 days)
3. Click "分析趨勢" button
4. You should see:
   - 6 charts loading
   - Data populating in charts
   - LLM explanations appearing under each chart

## Common Issues & Solutions

### Issue 1: CORS Errors

**Symptom**: Browser console shows CORS policy errors

**Solution**:
```bash
# Install CORS package
pip install django-cors-headers

# Verify CORS settings in backend/loanserp/base.py
# Should include:
# INSTALLED_APPS = [..., 'corsheaders', ...]
# MIDDLEWARE = [..., 'corsheaders.middleware.CorsMiddleware', ...]
# CORS_ALLOWED_ORIGINS = ['http://localhost:4200']
```

### Issue 2: No Data in Charts

**Symptom**: Charts are empty or show error

**Solution**:
1. Check if GSC data exists in database:
   ```bash
   python manage.py shell
   >>> from exposure.models import ExposureSnapshot
   >>> ExposureSnapshot.objects.count()
   ```
2. If no data, run GSC data pull:
   ```bash
   python manage.py gsc_pull --days=30
   ```

### Issue 3: LLM Service Errors

**Symptom**: "LLM 服務暫時無法使用" message

**Solution**:
1. Check API keys are set correctly
2. Verify Redis is running: `redis-cli ping`
3. Check LLM broker logs for errors

### Issue 4: Port Already in Use

**Symptom**: "Address already in use" error

**Solution**:
```bash
# Find process using port
lsof -ti:8000  # or 9001, 4200

# Kill process
kill -9 <PID>
```

## Development Workflow

### Running All Services

You'll need 3 terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
python manage.py runserver
```

**Terminal 2 - LLM Broker:**
```bash
cd geo_LLM_infra/llm_broker/app
uvicorn main:app --reload --port 9001
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm start
```

## Production Deployment

### Backend (Django)

```bash
# Collect static files
python manage.py collectstatic --noinput

# Use gunicorn
gunicorn loanserp.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### LLM Broker

```bash
# Use uvicorn with workers
uvicorn main:app --host 0.0.0.0 --port 9001 --workers 4
```

### Frontend

```bash
# Build for production
npm run build

# Serve with nginx or any static file server
# Files will be in dist/loanserp-frontend
```

## API Endpoints Reference

### Django Backend

- `GET /api/health` - Health check
- `GET /api/exposure/top5_timeseries?start=YYYY-MM-DD&end=YYYY-MM-DD` - Get top 5 keywords timeseries
- `GET /api/exposure/top5_compare?start=YYYY-MM-DD&end=YYYY-MM-DD` - Get comparison data

### LLM Broker

- `GET /v1/health` - Health check
- `POST /v1/summarize/trend` - Generate trend analysis

## Directory Structure

```
LoanSERP_claude-gemini-seo/
├── backend/                    # Django backend
│   ├── exposure/              # Main app
│   ├── loanserp/              # Project settings
│   ├── requirements.txt
│   └── requirements-cors.txt
├── geo_LLM_infra/
│   └── llm_broker/            # FastAPI LLM service
│       └── app/
│           └── main.py
├── frontend/                   # Angular 18 frontend
│   ├── src/
│   │   └── app/
│   │       ├── components/
│   │       ├── services/
│   │       └── models/
│   ├── package.json
│   └── angular.json
└── SETUP_GUIDE.md             # This file
```

## Next Steps

1. **Populate Data**: Run GSC data collection to populate your database
2. **Customize**: Adjust date ranges, chart types, and styling as needed
3. **Monitor**: Set up logging and monitoring for production
4. **Scale**: Add load balancing and caching strategies

## Support

For issues or questions, please refer to:
- Backend README: `backend/README.md`
- Frontend README: `frontend/README.md`
- LLM Broker: `geo_LLM_infra/llm_broker/app/main.py` (inline docs)

## License

Proprietary - LoanSERP Project
