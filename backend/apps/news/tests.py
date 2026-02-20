from django.test import TestCase
from apps.news.models import Article, Source, NewsCategory, NewsCategoryTranslation
from django.utils import timezone
from datetime import timedelta

class NewsCategoryTest(TestCase):
    """Test suite for the NewsCategory and its translations."""

    def setUp(self):
        self.category = NewsCategory.objects.create(
            name="BREAKING",
            slug="breaking",
            color="#FF0000"
        )
        self.translation = NewsCategoryTranslation.objects.create(
            category=self.category,
            lang="zh-TW",
            name="即時快訊"
        )

    def test_category_creation(self):
        """Test basic category fields."""
        self.assertEqual(self.category.name, "BREAKING")
        self.assertEqual(self.category.slug, "breaking")

    def test_category_translation(self):
        """Test if translation is correctly linked and retrievable."""
        trans = self.category.translations.get(lang="zh-TW")
        self.assertEqual(trans.name, "即時快訊")
        self.assertEqual(str(trans), "BREAKING (zh-TW)")

class ArticleModelTest(TestCase):
    """Test suite for the Article model."""

    def setUp(self):
        self.source = Source.objects.create(
            name="Motorsport",
            slug="motorsport",
            feed_url="https://example.com/rss"
        )
        self.article = Article.objects.create(
            source=self.source,
            original_lang="en",
            original_title="Verstappen Wins Bahrain",
            original_slug="verstappen-wins-bahrain",
            original_body="Full race report here...",
            published_at=timezone.now(),
            simhash="f1f1f1f1f1f1f1f1" # 測試 SimHash 存儲
        )

    def test_article_creation(self):
        """Test article creation and default fields."""
        self.assertEqual(self.article.original_title, "Verstappen Wins Bahrain")
        self.assertEqual(self.article.simhash, "f1f1f1f1f1f1f1f1")
        self.assertTrue(self.article.is_published)

    def test_article_source_relation(self):
        """Test relationship between article and its source."""
        self.assertEqual(self.article.source.name, "Motorsport")
        self.assertEqual(self.source.articles.count(), 1)
