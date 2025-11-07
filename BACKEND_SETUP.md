# Backend Setup Guide - Fixed Frontend Communication

This guide explains how to set up and run the LoanSERP backend services to work with the Angular frontend.

## Problem Fixed

The issue was that the frontend couldn't communicate with the backend due to:
1. Missing `.env` files with configuration
2. Missing CORS middleware in the FastAPI service
3. Missing credentials files

All of these have been fixed! ✅

## Architecture

The project has **two backend services**:

1. **Django Backend** (Port 8000)
   - Main API for exposure data, GSC integration
   - Endpoints: `/api/exposure/*`, `/api/health`

2. **LLM Broker (FastAPI)** (Port 9001)
   - AI-powered trend analysis using Gemini + Claude
   - Endpoints: `/v1/summarize/trend`, `/v1/health`

## Prerequisites

1. **Docker & Docker Compose** (for Postgres + Redis)
2. **Python 3.11+**
3. **Node.js 18+** (for Angular frontend)

## Quick Start

### 1. Start Docker Services (Required!)

```bash
cd docker
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (ports 6379)

Verify they're running:
```bash
docker-compose ps
```

### 2. Install Python Dependencies

**For Django Backend:**
```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-cors.txt
```

**For LLM Broker:**
```bash
cd ../geo_LLM_infra/llm_broker
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
cd backend
python manage.py migrate
```

### 4. Start Backend Services

**Option A: Start All Services (Recommended)**
```bash
# From project root
./start-all.sh
```

**Option B: Start Services Individually**

Terminal 1 - Django:
```bash
./start-backend.sh
```

Terminal 2 - FastAPI:
```bash
./start-llm-broker.sh
```

### 5. Verify Services Are Running

**Django Backend:**
```bash
curl http://localhost:8000/api/health
# Should return: {"ok": true}
```

**LLM Broker:**
```bash
curl http://localhost:9001/v1/health
# Should return: {"ok": true, "service": "LoanSERP LLM Broker", ...}
```

### 6. Start Frontend

```bash
cd frontend
npm install
npm start
```

Frontend will be available at: http://localhost:4200

## Configuration Files Created

### 1. `.env` (Django Backend)
Located at project root, contains:
- Django settings (SECRET_KEY, DEBUG, etc.)
- Database configuration (Postgres)
- Redis configuration
- Google Search Console credentials
- Business settings (keywords to track)

### 2. `geo_LLM_infra/.env` (LLM Broker)
Contains:
- Gemini API key
- Claude API key
- LLM broker settings
- Redis configuration (separate database)

### 3. Credentials Files
- `client_secret.json` - Google OAuth client credentials
- `backend/credentials/token.json` - Google OAuth token

## CORS Configuration

Both services are configured to accept requests from the Angular frontend:

**Django (backend/loanserp/base.py:79-83):**
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]
```

**FastAPI (geo_LLM_infra/llm_broker/app/main.py:335-344):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## API Endpoints

### Django Backend (http://localhost:8000/api)

- `GET /api/health` - Health check
- `GET /api/exposure/top5_timeseries?start=YYYY-MM-DD&end=YYYY-MM-DD` - Get top 5 keywords data
- `GET /api/exposure/top5_timeseries_auto?start=YYYY-MM-DD&end=YYYY-MM-DD&pull=true` - Auto-pull from GSC
- `GET /api/exposure/top5_compare?start=YYYY-MM-DD&end=YYYY-MM-DD&normalized=false&cum=false&smooth=0` - Compare keywords

### LLM Broker (http://localhost:9001/v1)

- `GET /v1/health` - Health check
- `POST /v1/summarize/trend` - Generate AI trend analysis

## Troubleshooting

### Frontend can't connect to backend

1. **Check services are running:**
   ```bash
   # Check Django
   curl http://localhost:8000/api/health

   # Check FastAPI
   curl http://localhost:9001/v1/health
   ```

2. **Check browser console** for CORS errors

3. **Verify Docker services:**
   ```bash
   cd docker
   docker-compose ps
   ```

### Database errors

```bash
# Reset database
cd backend
python manage.py migrate --run-syncdb

# Create test data (optional)
python create_test_data.py
```

### Redis connection errors

```bash
# Check Redis is running
docker exec -it docker-redis-1 redis-cli ping
# Should return: PONG
```

### Google Search Console errors

The OAuth token may have expired. To refresh:
```bash
cd backend
python manage.py fetch_gsc_data --dry-run
```

## Development Tips

### Using Django Admin

```bash
# Create superuser
cd backend
python manage.py createsuperuser

# Access admin at: http://localhost:8000/admin/
```

### Manual GSC Data Pull

```bash
cd backend
python manage.py fetch_gsc_data --start 2024-01-01 --end 2024-01-31
```

### Testing LLM Integration

```bash
curl -X POST http://localhost:9001/v1/summarize/trend \
  -H "Content-Type: application/json" \
  -d '{
    "period": {"start": "2024-01-01", "end": "2024-01-07", "days": 7},
    "top_keywords": ["貸款", "房屋貸款"],
    "dates": ["2024-01-01", "2024-01-02"],
    "series": [
      {"name": "貸款", "data": [100, 150]},
      {"name": "房屋貸款", "data": [80, 120]}
    ]
  }'
```

## Port Summary

- **3000**: (unused)
- **4200**: Angular Frontend
- **5432**: PostgreSQL (Docker)
- **6379**: Redis (Docker)
- **8000**: Django Backend
- **9001**: FastAPI/LLM Broker

## Next Steps

1. Access the frontend at http://localhost:4200
2. The dashboard should now load data from the backend
3. Test the LLM analysis features

## Support

If you encounter issues:
1. Check all services are running
2. Review logs for errors
3. Verify environment variables are loaded
4. Ensure Docker services are healthy
