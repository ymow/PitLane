"""Tests for processor components."""
import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta

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
    
    def test_identical_content_produces_similar_hash(self):
        """Test that identical content produces the same hash."""
        content = "Hamilton wins the race at Monaco Grand Prix"
        hash1 = self.deduplicator.compute_hash(content)
        hash2 = self.deduplicator.compute_hash(content)
        self.assertEqual(hash1, hash2)
    
    def test_slightly_different_content_produces_similar_hash(self):
        """Test that slightly different content produces similar hashes."""
        content1 = "Hamilton wins the race at Monaco Grand Prix in Formula 1"
        content2 = "Hamilton wins the race at Monaco Grand Prix in F1"
        
        hash1 = self.deduplicator.compute_hash(content1)
        hash2 = self.deduplicator.compute_hash(content2)
        
        # Calculate Hamming distance
        hamming_distance = bin(int(hash1, 16) ^ int(hash2, 16)).count('1')
        
        # Should be within similarity threshold (< 3 bits difference)
        self.assertLess(hamming_distance, 3)
    
    def test_syndicated_content_detection(self):
        """Test detection of syndicated content with different titles."""
        # Same body, different titles (common in syndication)
        body = "Lewis Hamilton secured pole position for tomorrow's race after a brilliant qualifying session. The Mercedes driver was 0.3 seconds faster than his nearest rival."
        
        title1 = "Hamilton Takes Pole Position"
        title2 = "Lewis Hamilton Secures Front Row Start"
        
        content1 = f"{title1} {body}"
        content2 = f"{title2} {body}"
        
        is_duplicate = self.deduplicator.is_duplicate(content2, "en", existing_content=content1)
        self.assertTrue(is_duplicate, "Should detect syndicated content despite different titles")
    
    def test_different_articles_not_detected_as_duplicates(self):
        """Test that genuinely different articles are not flagged as duplicates."""
        content1 = "Hamilton wins the Monaco Grand Prix after starting from pole position"
        content2 = "Verstappen crashes out on lap 45 while fighting for second place"
        
        is_duplicate = self.deduplicator.is_duplicate(content2, "en", existing_content=content1)
        self.assertFalse(is_duplicate, "Different articles should not be flagged as duplicates")
    
    def test_database_duplicate_detection(self):
        """Test duplicate detection against existing database articles."""
        # Create an existing article
        existing_content = "Hamilton wins Monaco Grand Prix with brilliant drive"
        existing_hash = self.deduplicator.compute_hash(existing_content)
        
        Article.objects.create(
            source=self.source,
            original_lang="en",
            original_title="Hamilton Wins Monaco",
            original_body="with brilliant drive",
            original_url="https://example.com/1",
            published_at=timezone.now(),
            simhash=existing_hash
        )
        
        # Test new content that's similar
        new_content = "Hamilton wins Monaco Grand Prix with brilliant drive from pole"
        is_duplicate = self.deduplicator.is_duplicate(new_content, "en")
        
        self.assertTrue(is_duplicate, "Should detect duplicate against database content")


class EntityExtractionTests(TestCase):
    """Test context-aware entity extraction."""
    
    def setUp(self):
        # Create test F1 entities
        self.team = Team.objects.create(
            official_name="Williams Racing",
            base_name="Williams",
            slug="williams"
        )
        
        self.driver = Driver.objects.create(
            first_name="Lewis",
            last_name="Hamilton",
            slug="lewis-hamilton"
        )
        
        # Mock spacy nlp object
        self.mock_nlp = Mock()
        self.extractor = F1EntityExtractor(nlp=self.mock_nlp)
    
    def test_driver_extraction_in_f1_context(self):
        """Test that drivers are correctly identified in F1 context."""
        # Mock spacy output for "Hamilton wins the race"
        mock_doc = Mock()
        mock_entity = Mock()
        mock_entity.text = "Hamilton"
        mock_entity.label_ = "PERSON"
        mock_entity.start_char = 0
        mock_entity.end_char = 8
        mock_doc.ents = [mock_entity]
        
        self.mock_nlp.return_value = mock_doc
        
        title = "Hamilton wins the race"
        body = "Lewis Hamilton dominated from start to finish"
        
        entities = self.extractor.process_article(title, body)
        
        # Should extract the driver
        self.assertGreater(len(entities['drivers']), 0)
        extracted_driver = entities['drivers'][0]
        self.assertEqual(extracted_driver['entity'], self.driver)
    
    def test_team_extraction_in_f1_context(self):
        """Test that teams are correctly identified in F1 context."""
        mock_doc = Mock()
        mock_entity = Mock()
        mock_entity.text = "Williams"
        mock_entity.label_ = "ORG"
        mock_entity.start_char = 0
        mock_entity.end_char = 8
        mock_doc.ents = [mock_entity]
        
        self.mock_nlp.return_value = mock_doc
        
        title = "Williams struggles in qualifying"
        body = "The Williams team had a difficult session"
        
        entities = self.extractor.process_article(title, body)
        
        # Should extract the team
        self.assertGreater(len(entities['teams']), 0)
        extracted_team = entities['teams'][0]
        self.assertEqual(extracted_team['entity'], self.team)
    
    def test_false_positive_prevention(self):
        """Test that non-F1 Williams references are ignored."""
        # Create mock for "Serena Williams plays tennis"
        mock_doc = Mock()
        mock_entity = Mock()
        mock_entity.text = "Williams"
        mock_entity.label_ = "PERSON"  # Person, not organization
        mock_entity.start_char = 6
        mock_entity.end_char = 14
        mock_doc.ents = [mock_entity]
        
        self.mock_nlp.return_value = mock_doc
        
        title = "Serena Williams plays tennis"
        body = "Tennis star Serena Williams won her match"
        
        entities = self.extractor.process_article(title, body)
        
        # Should NOT extract Williams team (wrong context)
        williams_teams = [t for t in entities['teams'] if t['entity'] == self.team]
        self.assertEqual(len(williams_teams), 0, "Should not extract Williams team from tennis context")
    
    def test_context_scoring(self):
        """Test that entities found in F1 context get higher scores."""
        # Test content with clear F1 context
        title = "Hamilton wins Monaco Grand Prix"
        body = "Lewis Hamilton secured victory at the Monaco Grand Prix driving for Mercedes"
        
        mock_doc = Mock()
        mock_entity = Mock()
        mock_entity.text = "Hamilton"
        mock_entity.label_ = "PERSON"
        mock_entity.start_char = 0
        mock_entity.end_char = 8
        mock_doc.ents = [mock_entity]
        
        self.mock_nlp.return_value = mock_doc
        
        entities = self.extractor.process_article(title, body)
        
        if entities['drivers']:
            # Should have high confidence due to F1 context words
            driver_entity = entities['drivers'][0]
            # Context scoring logic would be in the actual implementation
            self.assertTrue(driver_entity.get('is_primary', False) or 
                          driver_entity.get('confidence', 0) > 0.7)


class DistributedLockingTests(TestCase):
    """Test distributed locking for concurrent processing."""
    
    @patch('apps.workers.tasks.fetch.redis_client')
    def test_lock_acquisition_prevents_duplicate_processing(self, mock_redis):
        """Test that acquiring a lock prevents duplicate processing."""
        from apps.workers.tasks.fetch import fetch_single_source
        
        # Mock successful lock acquisition
        mock_lock = Mock()
        mock_lock.acquire.return_value = True
        mock_redis.lock.return_value = mock_lock
        
        # Mock source
        with patch('apps.workers.tasks.fetch.Source.objects.get') as mock_get_source:
            mock_source = Mock()
            mock_source.slug = 'test-source'
            mock_source.feed_url = 'https://example.com/feed'
            mock_source.lang = 'en'
            mock_get_source.return_value = mock_source
            
            # Mock fetcher
            with patch('apps.workers.tasks.fetch.RSSFetcher') as mock_fetcher_class:
                mock_fetcher = Mock()
                mock_fetcher.fetch.return_value = []
                mock_fetcher_class.return_value = mock_fetcher
                
                # Call the function
                fetch_single_source('test-source')
                
                # Verify lock was acquired
                mock_redis.lock.assert_called_once()
                mock_lock.acquire.assert_called_once()
    
    @patch('apps.workers.tasks.fetch.redis_client')
    def test_lock_failure_aborts_processing(self, mock_redis):
        """Test that failing to acquire lock aborts processing."""
        from apps.workers.tasks.fetch import fetch_single_source
        
        # Mock failed lock acquisition
        mock_lock = Mock()
        mock_lock.acquire.return_value = False
        mock_redis.lock.return_value = mock_lock
        
        with patch('apps.workers.tasks.fetch.logger') as mock_logger:
            result = fetch_single_source('test-source')
            
            # Should log that processing was skipped
            mock_logger.info.assert_called_with('Fetch already in progress for test-source, skipping.')
    
    @patch('apps.workers.tasks.fetch.redis_client')
    def test_redis_connection_failure_proceeds_without_lock(self, mock_redis):
        """Test that Redis connection failure allows processing without lock."""
        from apps.workers.tasks.fetch import fetch_single_source
        import redis
        
        # Mock Redis connection error
        mock_redis.lock.side_effect = redis.exceptions.ConnectionError("Connection failed")
        
        with patch('apps.workers.tasks.fetch.Source.objects.get') as mock_get_source:
            mock_source = Mock()
            mock_source.slug = 'test-source'
            mock_get_source.return_value = mock_source
            
            with patch('apps.workers.tasks.fetch.RSSFetcher') as mock_fetcher_class:
                mock_fetcher = Mock()
                mock_fetcher.fetch.return_value = []
                mock_fetcher_class.return_value = mock_fetcher
                
                with patch('apps.workers.tasks.fetch.logger') as mock_logger:
                    # Should not raise exception, should log warning and proceed
                    fetch_single_source('test-source')
                    
                    # Check that warning was logged about Redis unavailability
                    warning_calls = [call for call in mock_logger.info.call_args_list 
                                   if 'Redis unavailable' in str(call)]
                    self.assertGreater(len(warning_calls), 0, "Should log Redis unavailability warning")


if __name__ == '__main__':
    unittest.main()