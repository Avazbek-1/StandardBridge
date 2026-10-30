"""
Management command: update_site_domain

Django Site modelining domain maydonini SITE_URL muhit o'zgaruvchisiga qarab avtomatik yangilaydi.
Bu Google OAuth (django-allauth) va email/Telegram havolalari to'g'ri ishlashi uchun juda muhim.
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
from urllib.parse import urlparse


class Command(BaseCommand):
    help = 'Updates Django Site domain from SITE_URL env variable'

    def handle(self, *args, **options):
        site_url = getattr(settings, 'SITE_URL', 'https://standardbridge.uz')
        parsed = urlparse(site_url)
        domain = parsed.netloc or parsed.path
        if domain:
            site, created = Site.objects.update_or_create(
                id=1,
                defaults={'domain': domain, 'name': 'StandardBridge'}
            )
            self.stdout.write(
                self.style.SUCCESS(f"Django Site domain updated to: {domain} (Created: {created})")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Could not parse domain from SITE_URL: {site_url}")
            )
