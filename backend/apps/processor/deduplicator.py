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

    # Hamming distance threshold, calibrated on this project's own corpus (2,095 articles, 79,800 pairs).
    # With word-bigram features the genuine near-duplicates sit at 0-9 bits and the nearest unrelated pair
    # at 14, so 10 separates them cleanly: 16/16 real duplicates caught, 0 false positives.
    # Do not raise this without re-measuring: with the old single-word features a threshold of 8 already
    # produced 5 false positives, all of them short non-English bodies (es/fr) with <25% word overlap.
    HAMMING_DISTANCE_THRESHOLD = 10

    #: Word n-gram size for SimHash features. Single words lose too much signal on the 60-70 word
    #: RSS teasers this project actually ingests, and the loss is worst in Spanish and French.
    FEATURE_NGRAM = 2

    def _get_features(self, text: str) -> list:
        """Tokenize text into overlapping word n-grams for SimHash.

        Bigrams keep local word order, which is what separates "different article, shared vocabulary"
        from "same article, reworded" on short multilingual bodies.
        """
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        words = text.split()
        n = self.FEATURE_NGRAM
        if len(words) < n:
            return words
        return [' '.join(words[i:i + n]) for i in range(len(words) - n + 1)]

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
