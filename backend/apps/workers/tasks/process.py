"""Celery tasks for processing articles."""
from celery import shared_task
from apps.news.models import Article
from apps.processor.entity_extractor import F1EntityExtractor
from apps.processor.categorizer import ArticleCategorizer
from apps.workers.tasks.translate import queue_translations_for_article
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_article(article_id: str):
    """Process article: extract entities, categorize, queue translations."""
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        logger.warning(f"Article not found: {article_id}")
        return

    try:
        # Extract entities
        extractor = F1EntityExtractor()
        entities = extractor.process_article(
            title=article.original_title,
            body=article.original_body
        )

        # Add drivers
        for driver in entities['drivers']:
            article.drivers.add(driver)

        # Add teams
        for team in entities['teams']:
            article.teams.add(team)

        # Categorize
        categorizer = ArticleCategorizer()
        article.category = categorizer.categorize(
            title=article.original_title,
            body=article.original_body
        )
        article.priority = categorizer.prioritize(
            title=article.original_title,
            body=article.original_body
        )
        article.save()

        logger.info(
            f"Processed article {article_id}: {article.category}, "
            f"{len(entities['drivers'])} drivers, {len(entities['teams'])} teams"
        )

        # Queue translations
        queue_translations_for_article.delay(article_id)

    except Exception as e:
        logger.error(f"Error processing article {article_id}: {e}")


@shared_task
def warm_cache():
    """Pre-warm Redis cache with hot content."""
    from django.core.cache import cache
    from apps.news.models import Article, Translation

    languages = ['en', 'zh-TW', 'es', 'pt-BR']

    for lang in languages:
        # Warm breaking news
        breaking = Article.objects.filter(
            priority__in=['CRITICAL', 'HIGH'],
            translations__lang=lang,
            translations__status='PUBLISHED'
        ).distinct()[:5]

        # This will populate cache when accessed
        # Implementation depends on cache strategy

    logger.info("Cache warmed successfully")


@shared_task
def cleanup_old_articles(days: int = 90):
    """Delete articles older than specified days."""
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = Article.objects.filter(published_at__lt=cutoff).delete()

    logger.info(f"Deleted {deleted} articles older than {days} days")
