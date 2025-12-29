from django.core.management.base import BaseCommand
from apps.news.models import Source
from apps.workers.tasks.fetch import fetch_single_source
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch news from active RSS sources'

    def handle(self, *args, **options):
        self.stdout.write('Starting news fetch (Sync mode)...')
        
        sources = Source.objects.filter(is_active=True)
        
        for source in sources:
            self.stdout.write(f'Fetching from {source.name}...')
            try:
                # Call the task function directly (not as background task)
                # Note: fetch_single_source handles duplicate checks and processing
                fetch_single_source(source.slug)
                self.stdout.write(self.style.SUCCESS(f'  - Processed {source.name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  - Error fetching {source.name}: {e}'))
                logger.error(f"Error fetching {source.name}: {e}")
        
        self.stdout.write(self.style.SUCCESS('Done.'))
