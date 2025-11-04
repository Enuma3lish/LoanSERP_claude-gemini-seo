from django.core.management.base import BaseCommand
from exposure.gsc_client import _load_credentials
class Command(BaseCommand):
    help = "Run OAuth flow for Google Search Console (Installed App)."
    def handle(self, *args, **kwargs):
        _load_credentials()
        self.stdout.write(self.style.SUCCESS("GSC OAuth success. token.json is saved."))
