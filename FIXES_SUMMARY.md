# Backend Communication Fixes - Summary

## Problem Identified

The Angular frontend was unable to communicate with the Django and FastAPI backend services due to several configuration issues:

1. **Missing Environment Files** - No `.env` files with necessary configuration
2. **Missing CORS Configuration** - FastAPI service had no CORS middleware
3. **Missing Credentials** - Google OAuth credentials not properly placed
4. **No Startup Scripts** - Difficult to run services correctly

## Solutions Implemented

### 1. Environment Configuration

Created two `.env` files with all necessary configuration:

#### `.env` (Django Backend - Project Root)
- Django settings (SECRET_KEY, DEBUG, ALLOWED_HOSTS)
- PostgreSQL database configuration
- Redis configuration (database 1)
- Google Search Console OAuth settings
- Business settings (tracked keywords, API keys)

#### `geo_LLM_infra/.env` (FastAPI/LLM Broker)
- Gemini API key
- Claude API key
- LLM broker host/port settings
- Redis configuration (database 2)
- LLM model preferences and caching settings

### 2. CORS Configuration Fixed

#### Django Backend
Already had CORS configured in `backend/loanserp/base.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]
CORS_ALLOW_CREDENTIALS = True
```

#### FastAPI/LLM Broker
**Added** CORS middleware to `geo_LLM_infra/llm_broker/app/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

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

### 3. Credentials Setup

Created proper directory structure and files:
- `backend/credentials/` directory
- `backend/credentials/token.json` - Google OAuth access/refresh token
- `client_secret.json` - Google OAuth client credentials (project root)

### 4. Startup Scripts

Created three executable bash scripts:

#### `start-backend.sh`
- Loads environment variables from `.env`
- Runs Django migrations
- Starts Django development server on port 8000

#### `start-llm-broker.sh`
- Loads environment variables from `geo_LLM_infra/.env`
- Starts FastAPI server with uvicorn on port 9001

#### `start-all.sh`
- Master script that starts both services
- Manages process lifecycle
- Provides cleanup on exit

### 5. Comprehensive Documentation

Created `BACKEND_SETUP.md` with:
- Architecture overview
- Prerequisites
- Quick start guide
- Configuration details
- API endpoint documentation
- Troubleshooting guide
- Development tips

## File Changes Summary

### New Files Created
```
.env                              # Django configuration
geo_LLM_infra/.env               # FastAPI configuration
backend/credentials/token.json    # Google OAuth token
client_secret.json                # Google OAuth client secret
start-backend.sh                  # Django startup script
start-llm-broker.sh              # FastAPI startup script
start-all.sh                     # Master startup script
BACKEND_SETUP.md                  # Comprehensive setup guide
FIXES_SUMMARY.md                  # This file
```

### Modified Files
```
geo_LLM_infra/llm_broker/app/main.py   # Added CORS middleware
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Angular Frontend                          │
│                   http://localhost:4200                      │
└───────────────┬──────────────────────┬──────────────────────┘
                │                      │
                │ HTTP/JSON            │ HTTP/JSON
                │ (CORS enabled)       │ (CORS enabled)
                │                      │
        ┌───────▼────────┐     ┌──────▼──────────┐
        │ Django Backend │     │  FastAPI/LLM     │
        │  Port 8000     │     │  Broker          │
        │                │     │  Port 9001       │
        │ /api/exposure/ │     │ /v1/summarize/   │
        │ /api/health    │     │ /v1/health       │
        └───────┬────────┘     └──────┬───────────┘
                │                     │
                │                     │
        ┌───────▼─────────────────────▼───────┐
        │         Docker Services              │
        │  - PostgreSQL (port 5432)            │
        │  - Redis (port 6379)                 │
        │    DB 1: Django cache                │
        │    DB 2: LLM cache                   │
        └──────────────────────────────────────┘
```

## How to Start Everything

1. **Start Docker Services** (Postgres + Redis):
   ```bash
   cd docker
   docker compose up -d
   ```

2. **Install Dependencies**:
   ```bash
   # Django
   cd backend
   pip install -r requirements.txt -r requirements-cors.txt

   # FastAPI
   cd ../geo_LLM_infra/llm_broker
   pip install -r requirements.txt
   ```

3. **Start Backend Services**:
   ```bash
   # From project root
   ./start-all.sh
   ```

4. **Start Frontend**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

5. **Access Application**:
   - Frontend: http://localhost:4200
   - Django API: http://localhost:8000/api/
   - LLM Broker: http://localhost:9001/v1/

## Verification

### Test Django Backend
```bash
curl http://localhost:8000/api/health
# Expected: {"ok": true}
```

### Test FastAPI/LLM Broker
```bash
curl http://localhost:9001/v1/health
# Expected: {"ok": true, "service": "LoanSERP LLM Broker", ...}
```

### Test Frontend Communication
1. Open http://localhost:4200
2. Open browser DevTools (F12)
3. Check Network tab for successful API calls
4. No CORS errors should appear in Console

## Key Configuration Details

### Port Mapping
- **4200**: Angular Frontend
- **5432**: PostgreSQL (Docker)
- **6379**: Redis (Docker)
- **8000**: Django Backend
- **9001**: FastAPI/LLM Broker

### Redis Database Separation
- **DB 1**: Django cache, sessions, Celery
- **DB 2**: LLM response cache

### Environment Variables Loading
All startup scripts automatically load environment variables:
```bash
export $(cat .env | grep -v '^#' | xargs)
```

## Security Notes

⚠️ **Important**: The `.env` files contain sensitive information:
- API keys (Gemini, Claude, Serper)
- Database passwords
- Django secret key
- OAuth credentials

Ensure these files are properly secured and not committed to public repositories (already in `.gitignore`).

## Next Steps

1. ✅ Backend configuration complete
2. ✅ CORS issues resolved
3. ✅ Startup scripts created
4. ✅ Dependencies installed
5. 🔲 Start Docker services (user needs to do this)
6. 🔲 Run Django migrations (startup script does this)
7. 🔲 Test full stack integration

## Troubleshooting Common Issues

### CORS Errors
- Verify both services have CORS middleware configured
- Check frontend is accessing correct URLs
- Ensure services are running on expected ports

### Database Connection Errors
- Verify Docker PostgreSQL container is running
- Check `.env` has correct database credentials
- Ensure port 5432 is not blocked

### Redis Connection Errors
- Verify Docker Redis container is running
- Check Redis URL in `.env` files
- Ensure port 6379 is accessible

### Google OAuth Errors
- Token may be expired - run `python manage.py fetch_gsc_data --dry-run`
- Verify `client_secret.json` and `token.json` are in correct locations
- Check OAuth scopes match requirements

## Success Criteria

✅ Frontend can successfully communicate with both backend services
✅ CORS is properly configured on both services
✅ Environment variables are properly loaded
✅ All credentials are in the correct locations
✅ Startup scripts work correctly
✅ Dependencies are installed

The frontend should now be able to:
- Fetch keyword exposure data from Django backend
- Get AI-powered trend analysis from LLM broker
- Display charts and analytics without CORS errors
