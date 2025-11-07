# geo_LLM_infra/llm_broker/app/main.py
# -*- coding: utf-8 -*-
"""
LoanSERP LLM Broker (FastAPI)
- 僅根據後端提供的 GSC Top-N 關鍵字曝光時序資料，產生「趨勢摘要 + 行動建議」
- 不上網，不抓內容
- 支援 Gemini 與 Claude（同時呼叫、回傳各自輸出與合併摘要）
- 使用 Redis 以「請求 payload 雜湊」為鍵做結果快取
"""

import os
import re
import json
import hashlib
import asyncio
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
import redis.asyncio as redis

# === LLM SDKs ===
from anthropic import AsyncAnthropic  # 需 anthropic>=0.30
import google.generativeai as genai    # 需 google-generativeai>=0.7

# -------------------------
# 環境變數
# -------------------------
APP_NAME = "LoanSERP LLM Broker"
HOST = os.getenv("LLM_BROKER_HOST", "0.0.0.0")
PORT = int(os.getenv("LLM_BROKER_PORT", "9001"))

REDIS_URL = os.getenv("REDIS_URL")
CACHE_TTL = int(os.getenv("LLM_CACHE_TTL_SEC", "259200"))  # 預設 3 天

# 例如: "gemini-2.0-flash,claude-3-5-sonnet-20241022"
PREFERRED_MODELS = [x.strip() for x in os.getenv(
    "PREFERRED_MODELS", "gemini-2.0-flash,claude-3-5-sonnet-20241022"
).split(",") if x.strip()]

OUTPUT_LANG = os.getenv("OUTPUT_LANG", "zh-tw")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# -------------------------
# Redis client
# -------------------------
rcli = redis.from_url(REDIS_URL, decode_responses=True) if REDIS_URL else None

# -------------------------
# LLM clients
# -------------------------
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

anthropic_client = AsyncAnthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None


# -------------------------
# Pydantic Schemas
# -------------------------
class Period(BaseModel):
    start: str
    end: str
    days: int


class SeriesItem(BaseModel):
    name: str
    data: List[float]


class TrendRequest(BaseModel):
    period: Period
    top_keywords: List[str] = Field(..., min_items=1, max_items=10)
    dates: List[str]
    series: List[SeriesItem]                   # 長度需與 dates 對齊
    output_lang: str = OUTPUT_LANG             # "zh-tw" / "en"
    short_mid_long_base_days: int = 7          # 定義短期，則中期=2x，長期=3x
    mode: str = "no-external"                  # 僅使用提供資料
    use_cache: bool = True


class ProviderOut(BaseModel):
    provider: str
    model: str
    summary: str
    actions_short: List[str]
    actions_mid: List[str]
    actions_long: List[str]
    confidence: float


class TrendResponse(BaseModel):
    period: Period
    top_keywords: List[str]
    dates: List[str]
    provider_outputs: List[ProviderOut]
    consensus_summary: str
    notes: Optional[str] = None


# -------------------------
# Helpers
# -------------------------
def _hash_payload(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _pick_model(prefix: str, fallback: str) -> str:
    """從 PREFERRED_MODELS 中選第一個以 prefix 開頭的型號，否則用 fallback。"""
    for m in PREFERRED_MODELS:
        if m.lower().startswith(prefix):
            return m
    return fallback


def _validate_lengths(req: TrendRequest) -> None:
    """檢查每個 series 的 data 長度與 dates 是否一致。"""
    n = len(req.dates)
    for s in req.series:
        if len(s.data) != n:
            raise HTTPException(
                status_code=400,
                detail=f"Series '{s.name}' length {len(s.data)} != dates length {n}"
            )


_SECTION_RE = re.compile(r"^\s*\[(趨勢摘要|行動建議-短期|行動建議-中期|行動建議-長期|信心分數)\]\s*$", re.M)


def _parse_sections(text: str) -> Dict[str, Any]:
    """
    解析模型輸出的分段格式：
      [趨勢摘要]
      <paragraphs>

      [行動建議-短期]
      - a
      - b
      ...
      [行動建議-中期]
      ...
      [行動建議-長期]
      ...
      [信心分數]
      0.0~1.0 + 可選理由
    若模型未嚴格遵守格式，進行寬鬆抽取。
    """
    result = {
        "summary": text.strip(),
        "short": [],
        "mid": [],
        "long": [],
        "confidence": None,
    }

    parts = list(_SECTION_RE.finditer(text))
    if not parts:
        # 寬鬆抽取條列為行動建議
        bullets = [ln.strip()[2:].strip() for ln in text.splitlines() if ln.strip().startswith(("- ", "• "))]
        # 粗分成短中長（各 1/3）
        if bullets:
            k = max(1, len(bullets) // 3)
            result["short"] = bullets[:k]
            result["mid"] = bullets[k:2 * k]
            result["long"] = bullets[2 * k:]
        return result

    # 有標題情況，切段
    sections: Dict[str, str] = {}
    for i, m in enumerate(parts):
        title = m.group(1)
        start = m.end()
        end = parts[i + 1].start() if i + 1 < len(parts) else len(text)
        sections[title] = text[start:end].strip()

    def _bullets(body: str) -> List[str]:
        out = []
        for ln in body.splitlines():
            ln = ln.strip()
            if ln.startswith(("- ", "• ")):
                out.append(ln[2:].strip())
        return out

    if "趨勢摘要" in sections and sections["趨勢摘要"]:
        result["summary"] = sections["趨勢摘要"].strip()

    if "行動建議-短期" in sections:
        result["short"] = _bullets(sections["行動建議-短期"])
    if "行動建議-中期" in sections:
        result["mid"] = _bullets(sections["行動建議-中期"])
    if "行動建議-長期" in sections:
        result["long"] = _bullets(sections["行動建議-長期"])
    if "信心分數" in sections:
        # 嘗試抽出 0~1 間的小數
        m = re.search(r"([01](?:\.\d+)?)", sections["信心分數"])
        if m:
            try:
                result["confidence"] = max(0.0, min(1.0, float(m.group(1))))
            except Exception:
                pass

    return result


def build_prompt(req: TrendRequest) -> str:
    """系統提示：要求模型根據曝光時序資料，輸出固定格式的摘要與建議。"""
    return f"""
你是一位專業的銀行貸款(個人信貸，與房屋貸款)理財分析師。請用 {req.output_lang} 回答。
資料來源：請使用者提供的 Google Search Console 關鍵字「曝光」時間序列與上網檢索或引用外部新聞。
目標：
1) 描述在 {req.period.start} 至 {req.period.end} 期間的趨勢與變化與影響該變化的重大事件噢政策。
2) 比較 Top-{len(req.top_keywords)} 關鍵字的相對表現（成長/衰退、彼此交叉）。
3) 依據使用者定義的短/中/長期（短={req.short_mid_long_base_days}天；中=2x；長=3x），提出具體行動建議（行動關於用甚麼當作開頭讓使用者願意點進來我們的網站，與個人銀行貸款相關產品的推廣，如何達到最高效益）。
4) 提供不超過一段的風險/不確定性說明（如資料天數不足、總量波動、季節性等）。

請嚴格使用以下格式輸出（若無內容亦請保留標題）：
[趨勢摘要]
<多段落敘述>

[行動建議-短期]
- <建議1>
- <建議2>

[行動建議-中期]
- <建議1>
- <建議2>

[行動建議-長期]
- <建議1>
- <建議2>

[信心分數]
0.0~1.0（請量化信心，並簡要說明理由）
""".strip()


# -------------------------
# 供應商呼叫
# -------------------------
async def call_gemini(req: TrendRequest) -> Optional[ProviderOut]:
    if not GEMINI_API_KEY:
        return None
    model_name = _pick_model("gemini", "gemini-2.5-flash")
    model = genai.GenerativeModel(model_name)
    prompt = build_prompt(req)

    # 把時序資料以 JSON 一起提供
    context = {
        "period": req.period.model_dump(),
        "top_keywords": req.top_keywords,
        "dates": req.dates,
        "series": [s.model_dump() for s in req.series],
    }

    # google-generativeai 是同步；改在執行緒避免阻塞事件圈
    import functools
    loop = asyncio.get_event_loop()
    resp = await loop.run_in_executor(
        None, functools.partial(model.generate_content, [{"text": prompt}, {"text": json.dumps(context, ensure_ascii=False)}])
    )
    text = (getattr(resp, "text", "") or "").strip()
    parsed = _parse_sections(text)

    return ProviderOut(
        provider="gemini",
        model=model_name,
        summary=parsed["summary"],
        actions_short=parsed["short"],
        actions_mid=parsed["mid"],
        actions_long=parsed["long"],
        confidence=parsed["confidence"] if parsed["confidence"] is not None else 0.65,
    )


async def call_claude(req: TrendRequest) -> Optional[ProviderOut]:
    if not anthropic_client:
        return None
    model_name = _pick_model("claude", "claude-3-5-sonnet-20241022")
    prompt = build_prompt(req)
    context = {
        "period": req.period.model_dump(),
        "top_keywords": req.top_keywords,
        "dates": req.dates,
        "series": [s.model_dump() for s in req.series],
    }

    msg = await anthropic_client.messages.create(
        model=model_name,
        max_tokens=1400,
        temperature=0.4,
        system="You are an expert SEO analyst. Do NOT browse the web. Only use provided data.",
        messages=[{"role": "user", "content": f"{prompt}\n\n[DATA]\n{json.dumps(context, ensure_ascii=False)}"}],
    )
    # 取出文字片段
    chunks = []
    for b in getattr(msg, "content", []):
        if getattr(b, "type", "") == "text":
            chunks.append(getattr(b, "text", ""))
    text = "\n".join(chunks).strip()
    parsed = _parse_sections(text)

    return ProviderOut(
        provider="claude",
        model=model_name,
        summary=parsed["summary"],
        actions_short=parsed["short"],
        actions_mid=parsed["mid"],
        actions_long=parsed["long"],
        confidence=parsed["confidence"] if parsed["confidence"] is not None else 0.7,
    )


def make_consensus(outputs: List[ProviderOut]) -> str:
    """
    最小可行的「合併摘要」：直接串接不同供應商的摘要段落（可再演進為加權/去重）。
    """
    parts = []
    for o in outputs:
        if not o:
            continue
        parts.append(f"【{o.provider}】\n{o.summary}\n")
    return "\n".join(parts).strip()


# -------------------------
# FastAPI App
# -------------------------
app = FastAPI(title=APP_NAME)

# Configure CORS
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


@app.get("/v1/health")
async def health():
    return {
        "ok": True,
        "service": APP_NAME,
        "providers": {
            "gemini": bool(GEMINI_API_KEY),
            "claude": bool(CLAUDE_API_KEY),
        },
        "cache": bool(rcli is not None),
    }


@app.post("/v1/summarize/trend", response_model=TrendResponse)
async def summarize_trend(req: TrendRequest):
    # 基本資料檢查
    import traceback
    try:
        print(f"[DEBUG] Received request: period={req.period}, top_keywords={req.top_keywords}, dates_len={len(req.dates)}, series_len={len(req.series)}")
        for i, s in enumerate(req.series):
            print(f"[DEBUG] Series[{i}]: name={s.name}, data_len={len(s.data)}")
        _validate_lengths(req)
    except HTTPException as e:
        print(f"[ERROR] HTTPException: {e.detail}")
        traceback.print_exc()
        raise
    except ValidationError as e:
        print(f"[ERROR] ValidationError: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")

    payload = req.model_dump()
    cache_key = "llm:trend:" + _hash_payload(payload)

    # 讀取快取
    if req.use_cache and rcli is not None:
        cached = await rcli.get(cache_key)
        if cached:
            try:
                return json.loads(cached)
            except Exception:
                pass

    # 準備 LLM 呼叫
    calls = []
    print(f"[DEBUG] GEMINI_API_KEY configured: {bool(GEMINI_API_KEY)}")
    print(f"[DEBUG] CLAUDE_API_KEY configured: {bool(CLAUDE_API_KEY)}")
    if GEMINI_API_KEY:
        print("[DEBUG] Adding Gemini call")
        calls.append(call_gemini(req))
    if CLAUDE_API_KEY:
        print("[DEBUG] Adding Claude call")
        calls.append(call_claude(req))

    if not calls:
        print("[ERROR] No LLM provider available")
        raise HTTPException(status_code=400, detail="No LLM provider available (set GEMINI_API_KEY and/or CLAUDE_API_KEY).")

    # 并發呼叫；若單一供應商失敗，不影響另一個
    print(f"[DEBUG] Calling {len(calls)} LLM provider(s)")
    results = await asyncio.gather(*calls, return_exceptions=True)
    print(f"[DEBUG] Got {len(results)} results")
    outputs: List[ProviderOut] = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            # 不中斷；略過失敗供應商
            print(f"[ERROR] Provider {i} failed: {type(r).__name__}: {str(r)}")
            import traceback
            traceback.print_exc()
            continue
        if r:
            print(f"[DEBUG] Provider {i} succeeded: {r.provider}")
            outputs.append(r)

    if not outputs:
        print("[ERROR] All LLM providers failed")
        raise HTTPException(status_code=502, detail="All LLM providers failed.")

    resp = TrendResponse(
        period=req.period,
        top_keywords=req.top_keywords,
        dates=req.dates,
        provider_outputs=outputs,
        consensus_summary=make_consensus(outputs),
        notes="本結果僅依據提供的曝光時序資料，不含外部新聞。",
    )

    # 寫入快取
    if rcli is not None:
        try:
            await rcli.setex(cache_key, CACHE_TTL, json.dumps(resp.model_dump(), ensure_ascii=False))
        except Exception:
            pass

    return resp
