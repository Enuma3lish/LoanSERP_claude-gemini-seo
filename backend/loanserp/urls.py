from django.contrib import admin
from django.urls import path, include
from exposure.views import health, top5_timeseries, top5_timeseries_csv, top5_compare, top5_timeseries_auto

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health", health),
    path("api/exposure/top5_timeseries", top5_timeseries),            # JSON 給前端畫圖 (no auto-pull)
    path("api/exposure/top5_timeseries_auto", top5_timeseries_auto),  # JSON with auto-pull from GSC
    path("api/exposure/top5_timeseries.csv", top5_timeseries_csv),    # 仍保留 CSV 下載
    path("api/exposure/top5_compare", top5_compare),
]
