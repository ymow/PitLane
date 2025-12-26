"""Celery tasks for fetching RSS feeds."""
import logging
import redis
import hashlib
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from apps.fetcher.rss import RSSFetcher
from apps.fetcher.sources import SOURCES
from apps.news.models import Article, Source
from apps.workers.tasks.process import process_article
from apps.processor.deduplicator import Deduplicator

logger = logging.getLogger(__name__)

# Initialize Redis client for locking
redis_client = redis.from_url(getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0'))


@shared_task(bind=True, max_retries=3)
def fetch_sources_by_priority(self, source_slugs: list):
    """Fetch articles from multiple sources."""
    for slug in source_slugs:
        fetch_single_source.delay(slug)


@shared_task(bind=True, max_retries=3)
def fetch_single_source(self, source_slug: str):
    """Fetch articles from a single RSS source with distributed locking."""
    # 1. Acquire Distributed Lock (Redlock-lite)
    # Prevents multiple workers from fetching the same source at the same time
    lock_key = f"lock:fetch:{source_slug}"
    # Acquire lock for 5 minutes max
    lock = redis_client.lock(lock_key, timeout=300, blocking_timeout=2)
    
    acquired = False
    try:
        acquired = lock.acquire()
        if not acquired:
            logger.info(f"Fetch already in progress for {source_slug}, skipping.")
            return
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
        logger.info(f"Redis unavailable for locking on {source_slug}. Proceeding without lock: {e}")

    try:
        source = Source.objects.get(slug=source_slug, is_active=True)
    except Source.DoesNotExist:
        logger.warning(f"Source not found or inactive: {source_slug}")
        if acquired:
            lock.release()
        return

    try:
        # ... (rest of processing)
        fetcher = RSSFetcher(source.feed_url)
        items = fetcher.fetch()
        deduplicator = Deduplicator()

        new_count = 0
        for item in items:
            # Check if already exists (External ID)
            if Article.objects.filter(external_id=item.external_id).exists():
                continue

            # Check content duplication (Cross-source)
            # Combine title and body for fingerprinting
            content_text = f"{item.title} {item.body}"
            is_duplicate = deduplicator.is_duplicate(content_text, source.lang)
            
            # Compute Hash for storage
            content_hash = deduplicator.compute_hash(content_text)

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
                featured_image_url=item.image_url,
                is_duplicate=is_duplicate,
                simhash=content_hash
            )

            # Only process if NOT a duplicate
            if not is_duplicate:
                try:
                    process_article.delay(article.id)
                except Exception as e:
                    logger.info(f"Queue unavailable, processing article {article.id} synchronously: {e}")
                    from apps.workers.tasks.process import process_article as process_sync
                    process_sync(article.id)
                new_count += 1
            else:
                logger.info(f"Skipped processing for duplicate: {item.title}")

        logger.info(f"Fetched {new_count} new (unique) articles from {source_slug}")

    except Exception as exc:
        logger.error(f"Error fetching {source_slug}: {exc}")
        # Only retry if it's a celery task context
        if hasattr(self, 'request') and self.request.id:
            self.retry(exc=exc, countdown=60)
    finally:
        # Always release the lock if it was acquired
        try:
            if acquired:
                lock.release()
        except Exception:
            pass


@shared_task(bind=True, max_retries=3)
def fetch_all_active_sources(self):
    """Fetch from all active sources (emergency/manual trigger)."""
    sources = Source.objects.filter(is_active=True).values_list('slug', flat=True)
    for slug in sources:
        fetch_single_source.delay(slug)
