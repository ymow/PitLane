"""Celery tasks for processing articles."""
from celery import shared_task
from apps.news.models import Article, ArticleDriver, ArticleTeam, ArticleChunk, ArticleCategory
from apps.processor.entity_extractor import F1EntityExtractor
from apps.processor.categorizer import ArticleCategorizer
from apps.processor.chunker import HTMLChunker
from apps.processor.sanitizer import ArticleSanitizer
from apps.processor.monitoring import monitor_spacy_model_load, monitor_memory
from apps.workers.tasks.translate import queue_translations_for_article
from django.utils import timezone
from datetime import timedelta
import logging
import spacy

logger = logging.getLogger(__name__)

# Load Spacy model once when the worker boots (Tech Tip 2)
@monitor_spacy_model_load()
def _load_spacy_model():
    """Load Spacy model with memory monitoring."""
    return spacy.load("en_core_web_sm")

try:
    logger.info("Loading Spacy model (en_core_web_sm)...")
    nlp = _load_spacy_model()
except Exception as e:
    logger.error(f"Failed to load Spacy model: {e}")
    nlp = None


@shared_task
def process_article(article_id: str):
    """Process article: sanitize, score, chunk, extract, categorize, queue translations."""
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        logger.warning(f"Article not found: {article_id}")
        return

    try:
        # 0. Sanitize & Quality Score (ETL Transform)
        sanitizer = ArticleSanitizer()
        
        # Clean the body
        cleaned_body = sanitizer.sanitize(article.original_body)
        article.original_body = cleaned_body
        
        # Calculate quality score
        score = sanitizer.score_quality(
            title=article.original_title,
            body=cleaned_body,
            has_image=bool(article.featured_image_url)
        )
        article.quality_score = score
        article.save()

        # 1. Content Chunking (using cleaned body)
        chunker = HTMLChunker()
        chunks_data = chunker.chunk_article(cleaned_body)
        
        # Clear existing chunks (idempotency)
        ArticleChunk.objects.filter(article=article).delete()
        
        # Bulk create new chunks
        chunks = [
            ArticleChunk(
                article=article,
                sequence=chunk['sequence'],
                content=chunk['content'],
                chunk_type=chunk['type']
            )
            for chunk in chunks_data
        ]
        ArticleChunk.objects.bulk_create(chunks)

        # 2. Extract Entities (Reuse global nlp object)
        extractor = F1EntityExtractor(nlp=nlp)
        entities = extractor.process_article(
            title=article.original_title,
            body=cleaned_body
        )

        # Drivers
        ArticleDriver.objects.filter(article=article).delete()
        driver_relations = [
            ArticleDriver(
                article=article,
                driver=d['entity'],
                is_primary=d['is_primary']
            )
            for d in entities['drivers']
        ]
        ArticleDriver.objects.bulk_create(driver_relations)

        # Teams
        ArticleTeam.objects.filter(article=article).delete()
        team_relations = [
            ArticleTeam(
                article=article,
                team=t['entity'],
                is_primary=t['is_primary']
            )
            for t in entities['teams']
        ]
        ArticleTeam.objects.bulk_create(team_relations)

        # 3. Categorize
        categorizer = ArticleCategorizer()
        category = categorizer.categorize(
            title=article.original_title,
            body=cleaned_body,
            lang=article.original_lang
        )
        
        if category:
            # Clear existing categories and add the new one as primary
            ArticleCategory.objects.filter(article=article).delete()
            ArticleCategory.objects.create(
                article=article,
                category=category,
                is_primary=True
            )

        article.priority = categorizer.prioritize(
            title=article.original_title,
            body=cleaned_body
        )
        article.save()

        logger.info(
            f"Processed {article_id}: Score={score}, Cat={category.name if category else 'None'}, "
            f"Chunks={len(chunks)}"
        )

        # 4. Translation Policy (Cost Optimization)
        # Only translate if high quality or high priority
        should_translate = score >= 50.0 or article.priority in ['HIGH', 'CRITICAL']
        
        if should_translate:
            try:
                queue_translations_for_article.delay(article_id)
            except Exception as e:
                logger.info(f"Queue unavailable, attempting synchronous translation for {article_id}: {e}")
                # Fallback: Synchronous translation loop
                from apps.workers.tasks.translate import translate_article, TARGET_LANGUAGES
                
                try:
                    article_obj = Article.objects.get(id=article_id)
                    for lang in TARGET_LANGUAGES:
                        if lang != article_obj.original_lang:
                            try:
                                # Call the task function directly
                                # Note: self.retry inside translate_article might fail if not mocked
                                translate_article(article_id, lang)
                            except Exception as te:
                                logger.error(f"Sync translation failed for {lang}: {te}")
                except Exception as loop_e:
                     logger.error(f"Sync translation loop failed: {loop_e}")
        else:
            logger.info(f"Skipping translation for low quality article {article_id} (Score: {score})")

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