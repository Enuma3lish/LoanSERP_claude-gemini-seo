from datetime import date, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from exposure.gsc_client import fetch_daily_impressions
from exposure.models import Keyword, ExposureSnapshot

class Command(BaseCommand):
    help = "Pull daily impressions from GSC for configured keywords in the given period."

    def add_arguments(self, parser):
        parser.add_argument("--start", type=str, help="YYYY-MM-DD (default: today-N)")
        parser.add_argument("--end", type=str, help="YYYY-MM-DD (default: today)")
        parser.add_argument("--days", type=int, default=7, help="If no start/end, use last N days (max 90)")
        parser.add_argument("--only", type=str, help="Comma-separated subset of keywords (optional)")

    def handle(self, *args, **opts):
        end_str = opts.get("end")
        start_str = opts.get("start")
        days = min(int(opts.get("days", 7)), 90)
        if not end_str or not start_str:
            end = date.today()
            start = end - timedelta(days=days-1)
        else:
            start = date.fromisoformat(start_str)
            end = date.fromisoformat(end_str)
        if (end - start).days + 1 > 90:
            raise CommandError("Period cannot exceed 90 days.")

        # keyword list
        if opts.get("only"):
            kw_list = [k.strip() for k in opts["only"].split(",") if k.strip()]
        else:
            # from DB enabled keywords if present, otherwise from settings
            existing = list(Keyword.objects.filter(enabled=True).values_list("name", flat=True))
            kw_list = existing or settings.KEYWORD_TRACK_LIST

        self.stdout.write(f"Fetching {len(kw_list)} keywords from {start} to {end} ...")

        # ensure keywords exist in DB
        have = set(Keyword.objects.values_list("name", flat=True))
        for k in kw_list:
            if k not in have:
                Keyword.objects.create(name=k, enabled=True)
                have.add(k)

        start_iso, end_iso = start.isoformat(), end.isoformat()
        prop = settings.GSC_PROPERTY_URI

        cnt = 0
        for kw in kw_list:
            rows = fetch_daily_impressions(prop, kw, start_iso, end_iso)
            kobj = Keyword.objects.get(name=kw)
            for r in rows:
                ExposureSnapshot.objects.update_or_create(
                    date=r["date"], keyword=kobj,
                    defaults={"impressions": r["impressions"], "clicks": r["clicks"], "position": r["position"]}
                )
                cnt += 1
        self.stdout.write(self.style.SUCCESS(f"Done. Upserted rows: {cnt}"))
