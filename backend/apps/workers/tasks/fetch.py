"""Celery tasks for fetching RSS feeds."""
import logging
import redis
import hashlib
from celery import shared_task
from django.db.models import F
from django.utils import timezone
from django.conf import settings
from apps.fetcher.rss import RSSFetcher
from apps.fetcher.sources import SOURCES
from apps.news.models import Article, Source, IngestionStatus
from apps.workers.tasks.process import process_article
from apps.processor.deduplicator import Deduplicator

logger = logging.getLogger(__name__)

# Initialize Redis client for locking
redis_client = redis.from_url(getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0'))

# Priority tier thresholds (inclusive)
TIER_THRESHOLDS = {
    'high':   (90, 100),
    'medium': (70, 89),
    'low':    (0,  69),
}


@shared_task
def fetch_by_tier(tier: str):
    """Fetch all healthy active sources in a priority tier. Replaces fetch_sources_by_priority."""
    lo, hi = TIER_THRESHOLDS.get(tier, (0, 100))
    slugs = list(Source.objects.filter(
        is_active=True,
        is_healthy=True,
        priority__gte=lo,
        priority__lte=hi,
    ).values_list('slug', flat=True))
    for slug in slugs:
        fetch_single_source.delay(slug)
    logger.info(f"Queued {len(slugs)} sources for tier '{tier}'")


@shared_task(bind=True, max_retries=3)
def fetch_sources_by_priority(self, source_slugs: list):
    """Fetch articles from multiple sources. Kept for backwards compatibility."""
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
        fetcher = RSSFetcher(source.feed_url)
        items = fetcher.fetch()
        deduplicator = Deduplicator()

        new_count = 0
        for item in items:
            # Check if already exists (External ID)
            if Article.objects.filter(external_id=item.external_id).exists():
                continue

            # Check content duplication (Cross-source)
            content_text = f"{item.title} {item.body}"
            is_sim_duplicate = deduplicator.is_duplicate(content_text, source.lang)

            # Compute Hash for storage
            content_hash = deduplicator.compute_hash(content_text)

            initial_status = IngestionStatus.DUPLICATE if is_sim_duplicate else IngestionStatus.INGESTED

            # Always create article — duplicates are stored as reference corpus
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
                is_duplicate=is_sim_duplicate,
                simhash=content_hash,
                ingestion_status=initial_status,
                is_published=not is_sim_duplicate,
            )

            if not is_sim_duplicate:
                try:
                    process_article.delay(article.id)
                except Exception as e:
                    logger.warning(f"Queue unavailable, processing article {article.id} synchronously: {e}")
                    from apps.workers.tasks.process import process_article as process_sync
                    process_sync(article.id)
                new_count += 1
            else:
                logger.info(f"Stored duplicate (not processed): {item.title}")

        logger.info(f"Fetched {new_count} new (unique) articles from {source_slug}")

        # Update source health on success
        Source.objects.filter(slug=source_slug).update(
            consecutive_errors=0,
            is_healthy=True,
            last_fetched_at=timezone.now(),
            last_success_at=timezone.now(),
            total_articles_fetched=F('total_articles_fetched') + new_count,
        )

    except Exception as exc:
        logger.error(f"Error fetching {source_slug}: {exc}")

        # Update error counters
        Source.objects.filter(slug=source_slug).update(
            consecutive_errors=F('consecutive_errors') + 1,
            last_fetched_at=timezone.now(),
        )

        # Auto-pause after 5 consecutive errors
        paused = Source.objects.filter(
            slug=source_slug, consecutive_errors__gte=5, is_healthy=True
        ).update(is_healthy=False)
        if paused:
            logger.warning(f"Source '{source_slug}' auto-paused after 5 consecutive errors.")

        if hasattr(self, 'request') and self.request.id:
            self.retry(exc=exc, countdown=60)
    finally:
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


@shared_task
def probe_unhealthy_sources():
    """Probe all unhealthy sources. Restore to active if fetch succeeds."""
    slugs = list(Source.objects.filter(
        is_active=True,
        is_healthy=False,
    ).values_list('slug', flat=True))
    for slug in slugs:
        probe_single_source.delay(slug)
    logger.info(f"Probing {len(slugs)} unhealthy source(s)")


@shared_task(bind=True, max_retries=1)
def probe_single_source(self, source_slug: str):
    """Probe one unhealthy source; restore health if fetch succeeds."""
    try:
        Source.objects.get(slug=source_slug, is_active=True, is_healthy=False)
    except Source.DoesNotExist:
        return  # Already restored or deactivated

    try:
        source = Source.objects.get(slug=source_slug)
        fetcher = RSSFetcher(source.feed_url)
        items = fetcher.fetch()

        Source.objects.filter(slug=source_slug).update(
            is_healthy=True,
            consecutive_errors=0,
            last_fetched_at=timezone.now(),
            last_success_at=timezone.now(),
        )
        logger.info(f"Source '{source_slug}' restored (probe ok, {len(items)} items)")
    except Exception as exc:
        logger.warning(f"Source '{source_slug}' still unhealthy: {exc}")
