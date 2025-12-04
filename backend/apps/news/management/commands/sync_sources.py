"""Management command to sync RSS sources."""
from django.core.management.base import BaseCommand
from apps.fetcher.sources import SOURCES
from apps.news.models import Source
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Sync sources from configuration to database."""
    help = 'Sync RSS sources from sources.py to the database'

    def handle(self, *args, **options):
        """Execute the command."""
        created_count = 0
        updated_count = 0

        self.stdout.write("Syncing sources...")

        for slug, config in SOURCES.items():
            source, created = Source.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': config['name'],
                    'feed_url': config['feed_url'],
                    'lang': config['lang'],
                    'priority': config['priority'],
                    'fetch_interval': config['fetch_interval'],
                    'is_active': True
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {slug}"))
            else:
                updated_count += 1
                self.stdout.write(f"Updated: {slug}")

        # Optional: Deactivate sources not in config?
        # For now, we keep them but maybe log a warning or just leave them active.
        # If we wanted to be strict:
        # active_slugs = list(SOURCES.keys())
        # Source.objects.exclude(slug__in=active_slugs).update(is_active=False)

        self.stdout.write(self.style.SUCCESS(
            f"Sync complete. Created: {created_count}, Updated: {updated_count}"
        ))
