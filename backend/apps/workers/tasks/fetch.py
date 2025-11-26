"""Celery tasks for fetching RSS feeds."""
from celery import shared_task
from django.utils import timezone
from apps.fetcher.rss import RSSFetcher
from apps.fetcher.sources import SOURCES
from apps.news.models import Article, Source
from apps.workers.tasks.process import process_article
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def fetch_sources_by_priority(self, source_slugs: list):
    """Fetch articles from multiple sources."""
    for slug in source_slugs:
        fetch_single_source.delay(slug)


@shared_task(bind=True, max_retries=3)
def fetch_single_source(self, source_slug: str):
    """Fetch articles from a single RSS source."""
    try:
        source = Source.objects.get(slug=source_slug, is_active=True)
    except Source.DoesNotExist:
        logger.warning(f"Source not found or inactive: {source_slug}")
        return

    try:
        fetcher = RSSFetcher(source.feed_url)
        items = fetcher.fetch()

        new_count = 0
        for item in items:
            # Check if already exists
            if Article.objects.filter(external_id=item.external_id).exists():
                continue

            # Create article
            article = Article.objects.create(
                external_id=item.external_id,
                source=source,
                original_lang=source.lang,
                original_title=item.title,
                original_slug=item.slug,
                original_body=item.body,
                original_url=item.url,
                published_at=item.published_at,
                fetched_at=timezone.now(),
                image_url=item.image_url,
            )

            # Chain: process → translate
            process_article.delay(article.id)

            new_count += 1

        logger.info(f"Fetched {new_count} new articles from {source_slug}")

    except Exception as exc:
        logger.error(f"Error fetching {source_slug}: {exc}")
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def fetch_all_active_sources(self):
    """Fetch from all active sources (emergency/manual trigger)."""
    sources = Source.objects.filter(is_active=True).values_list('slug', flat=True)
    for slug in sources:
        fetch_single_source.delay(slug)
