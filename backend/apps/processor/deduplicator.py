"""Article Deduplication Service."""
from difflib import SequenceMatcher
from datetime import timedelta
from django.utils import timezone
from apps.news.models import Article
import logging

logger = logging.getLogger(__name__)


class Deduplicator:
    """Checks for duplicate articles across different sources."""

    SIMILARITY_THRESHOLD = 0.85  # 85% similarity means duplicate

    def is_duplicate(self, title: str, lang: str = 'en', lookback_hours: int = 24) -> bool:
        """
        Check if a similar article exists in the database.
        
        Args:
            title: The title of the new article.
            lang: Language code (only compare within same language).
            lookback_hours: How far back to check.
            
        Returns:
            True if duplicate found.
        """
        # 1. Exact Match Check (Fast)
        if Article.objects.filter(original_title__iexact=title, original_lang=lang).exists():
            return True

        # 2. Fuzzy Match Check (Slower)
        # Get recent articles in same language
        cutoff = timezone.now() - timedelta(hours=lookback_hours)
        recent_titles = Article.objects.filter(
            published_at__gte=cutoff,
            original_lang=lang
        ).values_list('original_title', flat=True)

        for existing_title in recent_titles:
            ratio = SequenceMatcher(None, title, existing_title).ratio()
            if ratio >= self.SIMILARITY_THRESHOLD:
                logger.info(f"Duplicate detected: '{title}' ~= '{existing_title}' ({ratio:.2f})")
                return True

        return False
