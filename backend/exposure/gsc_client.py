import os, datetime
from typing import Dict, List
from django.conf import settings
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = settings.GSC_SCOPES

def _load_credentials():
    token_path = settings.GSC_TOKEN_FILE
    client_path = settings.GSC_CLIENT_SECRETS_FILE
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_path, SCOPES)
            # WSL 可用本機瀏覽器授權
            creds = flow.run_local_server(port=0, prompt='consent')
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return creds

def _build_service(creds):
    # 新版 'searchconsole' v1，失敗時回退 'webmasters' v3
    try:
        return build('searchconsole', 'v1', credentials=creds, cache_discovery=False)
    except Exception:
        return build('webmasters', 'v3', credentials=creds, cache_discovery=False)

def fetch_daily_impressions(property_uri: str, keyword: str, start_date: str, end_date: str) -> List[Dict]:
    """
    回傳 rows: [{'date':'YYYY-MM-DD','impressions':int,'clicks':int,'position':float},...]
    """
    creds = _load_credentials()
    svc = _build_service(creds)
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["DATE"],
        "dimensionFilterGroups": [{
            "groupType":"AND",
            "filters":[{"dimension":"QUERY", "operator":"EQUALS", "expression": keyword}]
        }],
        "rowLimit": 1000
    }
    # 不同版本 method 名稱一致為 searchanalytics().query()
    resp = svc.searchanalytics().query(siteUrl=property_uri, body=body).execute()
    out = []
    for r in resp.get("rows", []):
        key_date = r.get("keys", [""])[0]
        out.append({
            "date": key_date,
            "impressions": int(r.get("impressions", 0)),
            "clicks": int(r.get("clicks", 0)),
            "position": float(r.get("position", 0.0)),
        })
    return out
