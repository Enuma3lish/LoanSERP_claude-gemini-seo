# Google Search Console Setup Guide

## Quick Setup (3 Steps)

### Step 1: Create Google Cloud Project & Enable API

1. Go to https://console.cloud.google.com/
2. Create new project (or select existing)
3. Enable **Google Search Console API**:
   - Go to: APIs & Services → Library
   - Search: "Search Console API"
   - Click: Enable

### Step 2: Create OAuth 2.0 Credentials

1. Go to: APIs & Services → Credentials
2. Click: **+ CREATE CREDENTIALS**
3. Select: **OAuth client ID**
4. Application type: **Desktop app**
5. Name: "LoanSERP Backend"
6. Click: **CREATE**
7. Click: **DOWNLOAD JSON**
8. Save as: `backend/credentials/client_secret.json`

### Step 3: Authenticate

```bash
cd backend
source .venv/bin/activate

# Create credentials directory
mkdir -p credentials

# Place your client_secret.json in credentials/

# Run authentication (opens browser)
python manage.py gsc_auth

# Follow browser prompts to authorize
# Token will be saved to: credentials/token.json
```

## Verify Setup

```bash
# Test GSC connection
python manage.py shell -c "from exposure.gsc_client import fetch_daily_impressions; print('GSC client loaded successfully')"

# Pull test data
python manage.py gsc_pull --days=7
```

## Configuration

Edit `backend/loanserp/base.py`:

```python
# Your GSC property (website)
GSC_PROPERTY_URI = "sc-domain:your-domain.com"
# or: "https://www.your-domain.com/"

# Keywords to track
KEYWORD_TRACK_LIST = [
    "貸款",
    "房屋貸款",
    "個人信貸",
    "車貸",
    "信用貸款"
]
```

## File Structure

```
backend/
├── credentials/           # OAuth credentials (gitignored)
│   ├── client_secret.json # From Google Cloud Console
│   └── token.json         # Auto-generated after auth
├── exposure/
│   ├── gsc_client.py     # GSC API client
│   └── gsc_auto_pull.py  # Auto-pull logic
└── manage.py
```

## Troubleshooting

### Issue: "credentials/client_secret.json not found"

**Solution:** Download from Google Cloud Console and place in correct location

```bash
cd backend
ls -la credentials/client_secret.json
# Should exist
```

### Issue: "Token expired"

**Solution:** Re-authenticate

```bash
cd backend
source .venv/bin/activate
python manage.py gsc_auth
```

### Issue: "Property not found"

**Solution:** Check your property URI matches GSC

1. Go to: https://search.google.com/search-console
2. Select your property
3. Check URL format:
   - Domain property: `sc-domain:example.com`
   - URL prefix: `https://www.example.com/`

## Security Notes

- ⚠️ **Never commit credentials/** to git
- ✅ Already in `.gitignore`
- ✅ Token auto-refreshes
- ✅ Credentials stored locally only

## Next Steps

Once authenticated:
1. ✅ Auto-pull will work automatically
2. ✅ Users can select any date range
3. ✅ Backend pulls missing data from GSC
4. ✅ Data cached in database for future requests

---

**Need Help?** See `AUTO_PULL_GSC_GUIDE.md` for complete documentation
