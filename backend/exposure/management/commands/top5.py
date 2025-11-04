from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db.models import Sum
from exposure.models import ExposureSnapshot, TrendAnalysisJob

class Command(BaseCommand):
    help = "Compute Top-5 keywords by total impressions in the period, restricted to tracked keywords."

    def add_arguments(self, parser):
        parser.add_argument("--start", type=str, help="YYYY-MM-DD")
        parser.add_argument("--end", type=str, help="YYYY-MM-DD")
        parser.add_argument("--days", type=int, default=7, help="If no start/end, use last N days (max 90)")

    def handle(self, *args, **opts):
        if opts.get("start") and opts.get("end"):
            start = date.fromisoformat(opts["start"])
            end = date.fromisoformat(opts["end"])
        else:
            end = date.today()
            start = end - timedelta(days=min(int(opts["days"]),90)-1)

        qs = (ExposureSnapshot.objects
              .filter(date__gte=start, date__lte=end)
              .values("keyword__name")
              .annotate(total_impr=Sum("impressions"))
              .order_by("-total_impr")[:5])

        top5 = [r["keyword__name"] for r in qs]
        job = TrendAnalysisJob.objects.create(
            days=(end-start).days+1, start_date=start, end_date=end, meta={"top5": top5}
        )
        self.stdout.write(self.style.SUCCESS(f"Top-5: {top5} (job_id={job.id})"))
