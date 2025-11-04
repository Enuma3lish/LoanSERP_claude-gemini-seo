from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import date, timedelta
from typing import List, Tuple, Dict
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from .models import ExposureSnapshot
from .gsc_auto_pull import auto_pull_if_needed
# from .crawler import search_and_collect  # Commented out - crawler module not needed for frontend
@api_view(["GET"])
def health(request):
    return Response({"ok": True})

def _drange(start: date, end: date) -> List[date]:
    d = start
    out = []
    while d <= end:
        out.append(d)
        d += timedelta(days=1)
    return out

def _parse_period(request) -> Tuple[date, date, int]:
    q = request.query_params
    try:
        days = int(q.get("days", 7))
    except Exception:
        days = 7
    days = max(1, min(days, 90))

    if q.get("start") and q.get("end"):
        start = date.fromisoformat(q["start"])
        end = date.fromisoformat(q["end"])
        total = (end - start).days + 1
        if total > 90:
            end = start + timedelta(days=89)
            total = 90
    else:
        end = date.today()
        start = end - timedelta(days=days - 1)
        total = days
    return start, end, total
def _sma(arr: List[float], w: int) -> List[float]:
    if w <= 1:
        return arr
    out, s = [], 0.0
    for i, v in enumerate(arr):
        s += v
        if i >= w: s -= arr[i - w]
        out.append(s / min(i + 1, w))
    return out
def _compute_top5_grid(start: date, end: date) -> Tuple[List[str], List[str], Dict[str, Dict[str, int]]]:
    """回傳 (top5, dates, grid)，grid[kw][date_iso] = impressions"""
    # 1) 先找期間合計曝光 Top-5
    agg = (ExposureSnapshot.objects
           .filter(date__gte=start, date__lte=end)
           .values("keyword__name")
           .annotate(total=Sum("impressions"))
           .order_by("-total")[:5])
    top5 = [a["keyword__name"] for a in agg]

    # 2) 取 Top-5 每日曝光
    rows = (ExposureSnapshot.objects
            .filter(date__gte=start, date__lte=end, keyword__name__in=top5)
            .values("date", "keyword__name")
            .annotate(impr=Sum("impressions")))

    dates = [d.isoformat() for d in _drange(start, end)]
    grid = {kw: {dt: 0 for dt in dates} for kw in top5}
    for r in rows:
        kw = r["keyword__name"]
        dt = r["date"].isoformat()
        if kw in grid and dt in grid[kw]:
            grid[kw][dt] = int(r["impr"] or 0)

    return top5, dates, grid

@api_view(["GET"])
def top5_timeseries(request):
    """JSON：前端畫 5 條線用"""
    start, end, total = _parse_period(request)
    top5, dates, grid = _compute_top5_grid(start, end)
    series = [{"name": kw, "data": [grid[kw][dt] for dt in dates]} for kw in top5]
    return Response({
        "period": {"start": start.isoformat(), "end": end.isoformat(), "days": total},
        "keywords": top5,
        "dates": dates,
        "series": series
    })

@api_view(["GET"])
def top5_timeseries_csv(request):
    """CSV 下載：date, kw1, kw2, kw3, kw4, kw5"""
    start, end, _ = _parse_period(request)
    top5, dates, grid = _compute_top5_grid(start, end)

    import csv, io
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["date"] + top5)
    for dt in dates:
        w.writerow([dt] + [grid[kw][dt] for kw in top5])

    resp = HttpResponse(buf.getvalue(), content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="top5_timeseries_{start}_{end}.csv"'
    return resp
@api_view(["GET"])
def top5_compare(request):
    """
    GET /api/exposure/top5_compare?days=7&normalized=false&cum=false&smooth=0
    回傳結構：
    {
      "period":{"start","end","days"},
      "keywords":["kw1",...,"kw5"],
      "dates":["YYYY-MM-DD",...],
      "series":[{"name":"kw1","data":[...]}, ...]  # 五條線一起
    }
    """
    start, end, total = _parse_period(request)
    top5, dates, grid = _compute_top5_grid(start, end)

    # 參數：占比 / 累積 / 平滑
    q = request.query_params
    normalized = q.get("normalized", "false").lower() in ("1","true","yes")
    cumulative = q.get("cum", "false").lower() in ("1","true","yes")
    smooth = int(q.get("smooth", "0") or 0)

    # 每日總量（供占比）
    day_totals = {dt: sum(grid[kw][dt] for kw in top5) for dt in dates}

    series = []
    for kw in top5:
        y = [grid[kw][dt] for dt in dates]
        if normalized:
            y = [ (v / day_totals[dt]) if day_totals[dt] > 0 else 0.0 for v, dt in zip(y, dates) ]
        if cumulative:
            c, yy = 0.0, []
            for v in y:
                c += v
                yy.append(c)
            y = yy
        if smooth and not cumulative:
            y = _sma([float(v) for v in y], smooth)
        series.append({"name": kw, "data": y})

    return Response({
        "period": {"start": start.isoformat(), "end": end.isoformat(), "days": total},
        "keywords": top5,
        "dates": dates,
        "series": series,
        "meta": {"normalized": normalized, "cumulative": cumulative, "smooth": smooth}
    })

def _parse_period_from_request(q):
    # 共用：解析期間，預設 days=7，上限 90
    try:
        days = int(q.get("days", 7))
    except Exception:
        days = 7
    days = max(1, min(days, 90))

    if q.get("start") and q.get("end"):
        start = date.fromisoformat(q["start"])
        end = date.fromisoformat(q["end"])
        total = (end - start).days + 1
        if total > 90:
            end = start + timedelta(days=89)
            total = 90
    else:
        end = date.today()
        start = end - timedelta(days=days - 1)
        total = days
    return start, end, total

# Note: crawl_top5_news_csv and crawl_top5_news_json functions removed
# They require the crawler module which is not available
# These endpoints are not used by the Angular frontend

@api_view(["GET"])
def top5_timeseries_auto(request):
    """
    Same as top5_timeseries, but automatically pulls from GSC if data is missing.

    GET /api/exposure/top5_timeseries_auto?start=YYYY-MM-DD&end=YYYY-MM-DD&pull=true

    Query params:
    - start, end: Date range
    - pull: 'true' to enable auto-pull (default: 'true')
    """
    start, end, total = _parse_period(request)

    # Check if auto-pull is enabled (default: true)
    enable_pull = request.query_params.get("pull", "true").lower() in ("true", "1", "yes")

    pull_status = None
    if enable_pull:
        try:
            # Check and pull if needed
            from django.conf import settings
            keywords = getattr(settings, 'KEYWORD_TRACK_LIST', [])
            pull_status = auto_pull_if_needed(start, end, keywords)
        except Exception as e:
            # If auto-pull fails, continue with existing data
            pull_status = {
                'had_data': False,
                'pulled': False,
                'error': str(e)
            }

    # Get the data (whether pulled or not)
    top5, dates, grid = _compute_top5_grid(start, end)
    series = [{"name": kw, "data": [grid[kw][dt] for dt in dates]} for kw in top5]

    response = {
        "period": {"start": start.isoformat(), "end": end.isoformat(), "days": total},
        "keywords": top5,
        "dates": dates,
        "series": series
    }

    # Add pull status if auto-pull was attempted
    if pull_status:
        response["pull_status"] = pull_status

    return Response(response)
