from django.db import models

class Keyword(models.Model):
    name = models.CharField(max_length=64, unique=True)
    enabled = models.BooleanField(default=True)
    def __str__(self): return self.name

class ExposureSnapshot(models.Model):
    date = models.DateField()
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(null=True, blank=True)
    position = models.FloatField(null=True, blank=True)
    class Meta:
        unique_together = ('date','keyword')

class TrendAnalysisJob(models.Model):
    days = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(null=True, blank=True)  # {'top5': [...]}
