from django.contrib import admin
from .models import Keyword, ExposureSnapshot, TrendAnalysisJob
@admin.register(Keyword)
class KAdmin(admin.ModelAdmin):
    list_display = ("name","enabled")
    search_fields = ("name",)
@admin.register(ExposureSnapshot)
class EAdmin(admin.ModelAdmin):
    list_display = ("date","keyword","impressions","clicks","position")
    list_filter = ("date","keyword")
@admin.register(TrendAnalysisJob)
class JAdmin(admin.ModelAdmin):
    list_display = ("id","days","start_date","end_date","created_at")
