# LoanSERP LLM Broker

FastAPI service that provides AI-powered trend analysis using Gemini and Claude.

## Quick Start

### Option 1: Use the automated script (Recommended)

```bash
./START_LLM_BROKER.sh
```

### Option 2: Manual start

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 9001 --reload
```

## Important Notes

### Correct Import Path

When running uvicorn, you must use `app.main:app` (not just `main:app`) because:
- The directory structure is: `llm_broker/app/main.py`
- You run uvicorn from the `llm_broker/` directory
- `app.main:app` means: import the `app` variable from `app/main.py`

### Common Errors

**Error: `ModuleNotFoundError: No module named 'app'`**

**Cause:** Running uvicorn with wrong syntax or from wrong directory

**Solution:**
```bash
# ❌ Wrong (from app/ directory)
cd app
uvicorn main:app

# ✅ Correct (from llm_broker/ directory)
cd llm_broker
uvicorn app.main:app --port 9001 --reload
```

## Environment Variables

Create a `.env` file in the `llm_broker/` directory:

```bash
# Required API Keys
GEMINI_API_KEY=your-gemini-api-key-here
CLAUDE_API_KEY=your-claude-api-key-here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Optional Settings
LLM_BROKER_HOST=0.0.0.0
LLM_BROKER_PORT=9001
OUTPUT_LANG=zh-tw
PREFERRED_MODELS=gemini-2.0-flash,claude-3-5-sonnet-20241022
```

## API Endpoints

### Health Check

```bash
GET /v1/health

Response:
{
  "ok": true,
  "service": "LoanSERP LLM Broker",
  "providers": {
    "gemini": true,
    "claude": true
  },
  "cache": true
}
```

### Summarize Trend

```bash
POST /v1/summarize/trend

Request Body:
{
  "period": {
    "start": "2025-10-01",
    "end": "2025-10-14",
    "days": 14
  },
  "top_keywords": ["貸款"],
  "dates": ["2025-10-01", "2025-10-02", ...],
  "series": [
    {
      "name": "貸款",
      "data": [1234, 1456, ...]
    }
  ],
  "output_lang": "zh-tw",
  "short_mid_long_base_days": 7,
  "use_cache": true
}

Response:
{
  "period": {...},
  "top_keywords": ["貸款"],
  "dates": [...],
  "provider_outputs": [
    {
      "provider": "gemini",
      "model": "gemini-2.0-flash",
      "summary": "趨勢分析摘要...",
      "actions_short": ["短期建議1", "短期建議2"],
      "actions_mid": ["中期建議1", "中期建議2"],
      "actions_long": ["長期建議1", "長期建議2"],
      "confidence": 0.85
    },
    {
      "provider": "claude",
      ...
    }
  ],
  "consensus_summary": "綜合摘要..."
}
```

## Dependencies

Install via pip:

```bash
pip install -r requirements.txt
```

Required packages:
- fastapi
- uvicorn[standard]
- pydantic
- anthropic
- google-generativeai
- redis

## Testing

```bash
# Check if server is running
curl http://localhost:9001/v1/health

# Should return:
# {"ok":true,"service":"LoanSERP LLM Broker",...}
```

## Troubleshooting

### Issue: No API keys

**Solution:** Set environment variables before starting:

```bash
export GEMINI_API_KEY="your-key"
export CLAUDE_API_KEY="your-key"
./START_LLM_BROKER.sh
```

### Issue: Redis connection error

**Solution:** Make sure Redis is running:

```bash
redis-server
# Or check if it's already running:
redis-cli ping
```

### Issue: Port already in use

**Solution:** Change the port or kill the existing process:

```bash
# Find process using port 9001
lsof -ti:9001

# Kill the process
kill -9 <PID>
```

## Architecture

```
Request (Frontend)
    ↓
FastAPI Endpoint
    ↓
Parallel LLM Calls
  ├── Gemini API
  └── Claude API
    ↓
Redis Cache (optional)
    ↓
Response (JSON)
```

## License

Proprietary - LoanSERP Project
