"""Article Deduplication Service using SimHash."""
import re
from simhash import Simhash
from datetime import timedelta
from django.utils import timezone
from apps.news.models import Article
from apps.processor.monitoring import monitor_memory
import logging

logger = logging.getLogger(__name__)


class Deduplicator:
    """Checks for duplicate articles using SimHash fingerprints."""

    # Hamming distance threshold (3 bits difference is standard for 'near-duplicate')
    HAMMING_DISTANCE_THRESHOLD = 3

    def _get_features(self, text: str) -> list:
        """Tokenize text into features for SimHash."""
        # Simple tokenization: lowercase, alpha-numeric only, 3-grams?
        # For simplicity, let's just use words.
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.split()

    def compute_hash(self, text: str) -> str:
        """Compute 64-bit SimHash as hex string."""
        if not text:
            return None
        features = self._get_features(text)
        if not features:
            return None
        # value is a 64-bit int
        hash_int = Simhash(features).value
        # Return hex string for DB storage (robust against signed/unsigned issues)
        return hex(hash_int)[2:]  # strip '0x'

    @monitor_memory("deduplicator")
    def is_duplicate(self, text: str, lang: str = 'en', lookback_hours: int = 24) -> bool:
        """
        Check if a similar article exists in the database.
        
        Args:
            text: The main content to check (Body prefered, else Title).
            lang: Language code.
            lookback_hours: How far back to check.
            
        Returns:
            True if duplicate found.
        """
        if not text:
            return False

        # 1. Compute Hash of incoming text
        new_hash_hex = self.compute_hash(text)
        if not new_hash_hex:
            return False
            
        new_hash_int = int(new_hash_hex, 16)

        # 2. Get recent candidates
        # Optimization: Only fetch hash field to minimize memory
        cutoff = timezone.now() - timedelta(hours=lookback_hours)
        candidates = Article.objects.filter(
            published_at__gte=cutoff,
            original_lang=lang,
            simhash__isnull=False
        ).values_list('simhash', flat=True)

        # 3. Compare Hamming Distance
        for cand_hex in candidates:
            try:
                cand_int = int(cand_hex, 16)
                # XOR to find difference bits
                xor_val = new_hash_int ^ cand_int
                # Count set bits (Hamming Distance)
                distance = bin(xor_val).count('1')
                
                if distance <= self.HAMMING_DISTANCE_THRESHOLD:
                    logger.info(f"Duplicate detected! Distance: {distance} (Hash: {new_hash_hex[:8]}...)")
                    return True
            except ValueError:
                continue

        return False
