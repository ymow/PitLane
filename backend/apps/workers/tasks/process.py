"""Celery tasks for processing articles."""
from celery import shared_task
from apps.news.models import Article, ArticleDriver, ArticleTeam, ArticleChunk, ArticleCategory, IngestionStatus
from apps.processor.entity_extractor import F1EntityExtractor
from apps.processor.categorizer import ArticleCategorizer
from apps.processor.chunker import HTMLChunker
from apps.processor.sanitizer import ArticleSanitizer
from apps.processor.monitoring import monitor_memory
from apps.workers.tasks.translate import queue_translations_for_article
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# Load Spacy model lazily
_nlp = None

def _get_nlp():
    """Get or load Spacy model."""
    global _nlp
    if _nlp is None:
        try:
            import spacy
            logger.info("Loading Spacy model (en_core_web_sm)...")
            _nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.debug(f"Failed to load Spacy model: {e}")
            _nlp = None
    return _nlp


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

        # Early exit for low quality articles — store but don't process further
        # DON-37: HIGH/CRITICAL priority articles bypass the quality gate
        if score < 30 and article.priority not in ('HIGH', 'CRITICAL'):
            article.ingestion_status = IngestionStatus.LOW_QUALITY
            article.is_published = False
            article.save(update_fields=['original_body', 'quality_score', 'ingestion_status', 'is_published'])
            logger.info(f"Article {article_id} marked LOW_QUALITY (score={score:.1f})")
            return

        # Note: save() deferred — merged with priority save below

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

        # 2. Extract Entities (Reuse NLP object)
        nlp = _get_nlp()
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

        # 4. Translation Policy (Cost Optimization)
        # Only translate if AI features are enabled AND (high quality or high priority)
        from django.conf import settings
        should_translate = settings.ENABLE_AI_FEATURES and (score >= 50.0 or article.priority in ['HIGH', 'CRITICAL'])

        # Set ingestion status based on translation decision
        if should_translate:
            article.ingestion_status = IngestionStatus.PUBLISHED
        else:
            article.ingestion_status = IngestionStatus.PROCESSED

        # Single save for all field changes
        article.save(update_fields=['original_body', 'quality_score', 'priority', 'ingestion_status'])

        logger.info(
            f"Processed {article_id}: Score={score}, Cat={category.name if category else 'None'}, "
            f"Chunks={len(chunks)}, Status={article.ingestion_status}"
        )
        
        if should_translate:
            try:
                queue_translations_for_article.delay(article_id)
            except Exception as e:
                logger.warning(f"Queue unavailable, attempting synchronous translation for {article_id}: {e}")
                # Fallback: Synchronous translation loop
                from apps.workers.tasks.translate import translate_article, TARGET_LANGUAGES
                
                try:
                    article_obj = Article.objects.get(id=article_id)
                    for lang in TARGET_LANGUAGES:
                        if lang != article_obj.original_lang:
                            try:
                                # Call the task function directly
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
    from apps.news.models import Article
    from apps.api.serializers import ArticleListSerializer

    languages = ['en', 'zh-TW', 'zh-CN', 'es', 'pt-BR', 'it', 'nl', 'de', 'ja', 'fr']

    for lang in languages:
        breaking = Article.objects.filter(
            priority__in=['CRITICAL', 'HIGH'],
            translations__lang=lang,
            translations__status='PUBLISHED'
        ).prefetch_related('translations', 'source', 'categories').distinct()[:5]

        serializer = ArticleListSerializer(breaking, many=True, context={'lang': lang})
        cache.set(f'breaking:{lang}', serializer.data, timeout=3600)

    logger.info("Cache warmed successfully")


@shared_task
def cleanup_old_articles(days: int = 90):
    """Delete articles older than specified days."""
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = Article.objects.filter(published_at__lt=cutoff).delete()

    logger.info(f"Deleted {deleted} articles older than {days} days")
