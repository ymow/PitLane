"""Tests for processor components."""
import unittest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.utils import timezone

from apps.processor.deduplicator import Deduplicator
from apps.processor.entity_extractor import F1EntityExtractor
from apps.news.models import Article, Source
from apps.teams.models import Driver, Team


class SimHashDeduplicationTests(TestCase):
    """Test SimHash-based deduplication functionality."""

    def setUp(self):
        self.deduplicator = Deduplicator()
        self.source = Source.objects.create(
            name="Test Source",
            slug="test-source",
            feed_url="https://example.com/feed",
            lang="en"
        )

    def test_identical_content_produces_same_hash(self):
        """Identical content must produce the exact same hash."""
        content = "Hamilton wins the race at Monaco Grand Prix"
        self.assertEqual(
            self.deduplicator.compute_hash(content),
            self.deduplicator.compute_hash(content),
        )

    def test_similar_long_content_within_threshold(self):
        """Long articles that differ by a few words should be within the 3-bit threshold.

        SimHash works best on content with >= ~50 words.
        Real RSS bodies are 200-1000+ words, so this mirrors production inputs.
        """
        base = (
            "Lewis Hamilton dominated the Monaco Grand Prix from start to finish, "
            "leading every lap after securing pole position on Saturday. "
            "The Mercedes driver controlled the race pace throughout, managing tyre "
            "degradation expertly to claim his eighth victory at the street circuit. "
            "Verstappen finished second after a late strategy call, while Norris "
            "completed the podium in third place for McLaren."
        )
        # One extra sentence — the bulk of the content is identical
        similar = base + " Hamilton dedicated the win to his team back at the factory."

        hash1 = self.deduplicator.compute_hash(base)
        hash2 = self.deduplicator.compute_hash(similar)
        distance = bin(int(hash1, 16) ^ int(hash2, 16)).count('1')

        self.assertLessEqual(
            distance, Deduplicator.HAMMING_DISTANCE_THRESHOLD,
            f"Expected Hamming distance <= {Deduplicator.HAMMING_DISTANCE_THRESHOLD}, got {distance}",
        )

    def test_clearly_different_content_exceeds_threshold(self):
        """Genuinely different articles must exceed the Hamming threshold."""
        content1 = (
            "Hamilton wins the Monaco Grand Prix after starting from pole position "
            "and leading every lap in a dominant display from Mercedes."
        )
        content2 = (
            "Verstappen crashes out on lap 45 while fighting for second place, "
            "a mechanical failure ending his championship hopes for the weekend."
        )
        hash1 = self.deduplicator.compute_hash(content1)
        hash2 = self.deduplicator.compute_hash(content2)
        distance = bin(int(hash1, 16) ^ int(hash2, 16)).count('1')

        self.assertGreater(
            distance, Deduplicator.HAMMING_DISTANCE_THRESHOLD,
            f"Expected Hamming distance > {Deduplicator.HAMMING_DISTANCE_THRESHOLD}, got {distance}",
        )

    def test_database_duplicate_detection(self):
        """is_duplicate() should find a near-identical article already in the DB."""
        existing_body = (
            "Lewis Hamilton secured pole position for the Monaco Grand Prix after "
            "a stunning final lap in Q3. The Mercedes driver was 0.3 seconds faster "
            "than his nearest rival Max Verstappen, with Lando Norris third for McLaren. "
            "Hamilton praised the team's setup work and said the car felt perfect "
            "around the narrow street circuit. It is his seventh pole at Monaco."
        )
        existing_hash = self.deduplicator.compute_hash(existing_body)

        Article.objects.create(
            source=self.source,
            original_lang="en",
            original_title="Hamilton Takes Monaco Pole",
            original_body=existing_body,
            original_url="https://example.com/1",
            published_at=timezone.now(),
            simhash=existing_hash,
        )

        # Syndicated copy: same body with one extra sentence appended
        new_body = existing_body + " The race takes place on Sunday at 15:00 local time."
        self.assertTrue(
            self.deduplicator.is_duplicate(new_body, "en"),
            "Should detect syndicated near-duplicate against DB content",
        )

    def test_empty_content_returns_false(self):
        """Empty string must never be flagged as a duplicate."""
        self.assertFalse(self.deduplicator.is_duplicate("", "en"))

    def test_compute_hash_returns_none_for_empty(self):
        """compute_hash on empty string returns None, not a hash."""
        self.assertIsNone(self.deduplicator.compute_hash(""))


class EntityExtractionTests(TestCase):
    """Test context-aware entity extraction (regex fallback path)."""

    def setUp(self):
        # Team: only required non-nullable fields
        self.team = Team.objects.create(
            code="WIL",
            base_name="Williams",
            country="United Kingdom",
            founded_year=1977,
        )
        # Driver: all required fields
        self.driver = Driver.objects.create(
            code="HAM",
            first_name="Lewis",
            last_name="Hamilton",
            full_name="Lewis Hamilton",
            nationality="British",
            date_of_birth="1985-01-07",
            status="ACTIVE",
        )
        # nlp=None forces the regex fallback path
        self.extractor = F1EntityExtractor(nlp=None)

    def test_driver_last_name_extracted(self):
        """Last name in title/body should resolve to the correct Driver entity."""
        entities = self.extractor.process_article(
            title="Hamilton wins the race",
            body="Lewis Hamilton dominated from start to finish at Monaco.",
        )
        driver_entities = [d['entity'] for d in entities['drivers']]
        self.assertIn(self.driver, driver_entities)

    def test_team_base_name_extracted(self):
        """Team base_name in title/body should resolve to the correct Team entity."""
        entities = self.extractor.process_article(
            title="Williams struggles in qualifying",
            body="The Williams team had a very difficult qualifying session today.",
        )
        team_entities = [t['entity'] for t in entities['teams']]
        self.assertIn(self.team, team_entities)

    def test_unrelated_content_extracts_nothing(self):
        """Content with no F1 entity names should return empty lists."""
        entities = self.extractor.process_article(
            title="Stock market hits all-time high",
            body="Investors celebrated as the S&P 500 reached record levels today.",
        )
        self.assertEqual(entities['drivers'], [])
        self.assertEqual(entities['teams'], [])

    def test_primary_flag_set_for_title_mention(self):
        """Entity mentioned in the title (score >= 10) should be marked is_primary."""
        entities = self.extractor.process_article(
            title="Hamilton takes pole at Monaco",
            body="Lewis Hamilton was fastest in qualifying for the Monaco Grand Prix.",
        )
        self.assertTrue(len(entities['drivers']) > 0)
        self.assertTrue(entities['drivers'][0]['is_primary'])


class DistributedLockingTests(TestCase):
    """Test distributed locking in the fetch task."""

    @patch('apps.workers.tasks.fetch.redis_client')
    def test_successful_lock_allows_processing(self, mock_redis):
        """Acquiring the lock permits the fetch to proceed."""
        from apps.workers.tasks.fetch import fetch_single_source

        mock_lock = Mock()
        mock_lock.acquire.return_value = True
        mock_redis.lock.return_value = mock_lock

        with patch('apps.workers.tasks.fetch.Source.objects.get') as mock_get:
            mock_source = Mock()
            mock_source.slug = 'test-source'
            mock_source.feed_url = 'https://example.com/feed'
            mock_source.lang = 'en'
            mock_get.return_value = mock_source

            with patch('apps.workers.tasks.fetch.RSSFetcher') as mock_fetcher_cls:
                mock_fetcher_cls.return_value.fetch.return_value = []
                fetch_single_source('test-source')

        mock_redis.lock.assert_called_once()
        mock_lock.acquire.assert_called_once()

    @patch('apps.workers.tasks.fetch.redis_client')
    def test_failed_lock_skips_processing(self, mock_redis):
        """Failing to acquire the lock aborts the fetch immediately."""
        from apps.workers.tasks.fetch import fetch_single_source

        mock_lock = Mock()
        mock_lock.acquire.return_value = False
        mock_redis.lock.return_value = mock_lock

        with patch('apps.workers.tasks.fetch.logger') as mock_logger:
            fetch_single_source('test-source')
            logged = ' '.join(str(c) for c in mock_logger.info.call_args_list)
            self.assertIn('skipping', logged)

    @patch('apps.workers.tasks.fetch.redis_client')
    def test_redis_acquire_error_proceeds_without_lock(self, mock_redis):
        """ConnectionError from lock.acquire() is caught; fetch continues gracefully."""
        import redis as redis_lib
        from apps.workers.tasks.fetch import fetch_single_source

        mock_lock = Mock()
        # Error on acquire(), not on lock() — matches the try/except in fetch.py
        mock_lock.acquire.side_effect = redis_lib.exceptions.ConnectionError("down")
        mock_redis.lock.return_value = mock_lock

        with patch('apps.workers.tasks.fetch.Source.objects.get') as mock_get:
            mock_source = Mock()
            mock_source.slug = 'test-source'
            mock_source.feed_url = 'https://example.com/feed'
            mock_source.lang = 'en'
            mock_get.return_value = mock_source

            with patch('apps.workers.tasks.fetch.RSSFetcher') as mock_fetcher_cls:
                mock_fetcher_cls.return_value.fetch.return_value = []
                with patch('apps.workers.tasks.fetch.logger') as mock_logger:
                    fetch_single_source('test-source')
                    logged = ' '.join(str(c) for c in mock_logger.info.call_args_list)
                    self.assertIn('Redis unavailable', logged)


if __name__ == '__main__':
    unittest.main()
