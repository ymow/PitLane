from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.news.models import Source, Article, ArticleCategory
from apps.fetcher.rss import RSSFetcher
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch news from active RSS sources'

    def handle(self, *args, **options):
        self.stdout.write('Starting news fetch...')
        
        sources = Source.objects.filter(is_active=True)
        total_new = 0
        
        for source in sources:
            self.stdout.write(f'Fetching from {source.name}...')
            try:
                fetcher = RSSFetcher(source.feed_url)
                items = fetcher.fetch()
                
                new_count = 0
                for item in items:
                    # Check if article already exists
                    if Article.objects.filter(external_id=item.external_id).exists():
                        continue
                        
                    # Create new article
                    article = Article(
                        source=source,
                        external_id=item.external_id,
                        original_lang=source.lang,
                        original_title=item.title,
                        original_slug=item.slug,
                        original_body=item.body,
                        original_url=item.url,
                        published_at=item.published_at,
                        featured_image_url=item.image_url,
                        priority='NORMAL'
                    )
                    article.save()
                    new_count += 1
                
                self.stdout.write(self.style.SUCCESS(f'  - Added {new_count} new articles'))
                total_new += new_count
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  - Error fetching {source.name}: {e}'))
                logger.error(f"Error fetching {source.name}: {e}")
        
        self.stdout.write(self.style.SUCCESS(f'Done. Total new articles: {total_new}'))
