"""Celery tasks for AI translation."""
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from apps.news.models import Article, Translation
from apps.translator.claude_service import ClaudeTranslator
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# Target languages for translation
TARGET_LANGUAGES = ['en', 'zh-TW', 'zh-CN', 'es', 'pt-BR', 'it', 'nl', 'de', 'ja', 'fr', 'tr', 'pl']


def get_translator():
    """Get Claude translator instance."""
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not configured")
        raise ValueError("ANTHROPIC_API_KEY not configured")
    return ClaudeTranslator(api_key=api_key)


@shared_task(bind=True, max_retries=3, rate_limit='10/m')
def translate_article(self, article_id: str, target_lang: str):
    """Translate article to target language."""
    # Check if API key is configured
    if not settings.ANTHROPIC_API_KEY:
        logger.warning(
            f'Translation skipped for article {article_id} to {target_lang} - '
            f'ANTHROPIC_API_KEY not configured. Add API key to .env to enable translations.'
        )
        return {
            'article_id': article_id,
            'lang': target_lang,
            'status': 'skipped',
            'reason': 'api_key_missing'
        }

    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        logger.warning(f"Article not found: {article_id}")
        return

    # Skip if already translated
    if Translation.objects.filter(article=article, lang=target_lang).exists():
        logger.info(f"Translation already exists: {article_id} → {target_lang}")
        return

    # Skip if same as original
    if article.original_lang == target_lang:
        # Create "translation" from original content
        Translation.objects.create(
            article=article,
            lang=target_lang,
            title=article.original_title,
            slug=article.original_slug,
            body=article.original_body,
            summary=article.original_summary,
            status='PUBLISHED',
            confidence_score=1.0,
            translator='original',
            translated_at=timezone.now(),
            published_at=timezone.now(),
        )
        return

    try:
        # Translate using Claude
        translator = get_translator()
        result = translator.translate(
            title=article.original_title,
            body=article.original_body,
            source_lang=article.original_lang,
            target_lang=target_lang,
        )

        # Determine status based on confidence
        status = 'PUBLISHED' if result.confidence >= 0.85 else 'DRAFT'

        # Save translation
        Translation.objects.create(
            article=article,
            lang=target_lang,
            title=result.title,
            slug=slugify(result.title),
            body=result.body,
            summary=result.summary,
            status=status,
            confidence_score=result.confidence,
            translator=f'Claude ({ClaudeTranslator.MODEL})',
            translated_at=timezone.now(),
            published_at=timezone.now() if status == 'PUBLISHED' else None,
        )

        logger.info(
            f"translate_cost article_id={article_id} lang={target_lang} "
            f"model={ClaudeTranslator.MODEL} "
            f"input_tokens={result.input_tokens} output_tokens={result.output_tokens}"
        )

        # Invalidate cache
        cache.delete(f'article:{article.original_slug}:{target_lang}')
        cache.delete(f'latest:news:{target_lang}')

        logger.info(f"Translated {article_id} → {target_lang} (confidence: {result.confidence})")

    except Exception as exc:
        import anthropic
        if isinstance(exc, anthropic.AuthenticationError):
            logger.error(f"Translation failed {article_id} → {target_lang}: Invalid API Key (401). Skipping.")
            return {
                'article_id': article_id,
                'lang': target_lang,
                'status': 'failed',
                'reason': 'authentication_error'
            }
        
        logger.error(f"Translation failed {article_id} → {target_lang}: {exc}")
        self.retry(exc=exc, countdown=120)


@shared_task
def queue_translations_for_article(article_id: str):
    """Queue translations for all target languages."""
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return

    for lang in TARGET_LANGUAGES:
        if lang != article.original_lang:
            translate_article.delay(article_id, lang)
