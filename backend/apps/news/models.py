"""
News app models for PitLane F1 platform.
"""
from django.db import models
from django.utils.text import slugify
from config.utils import generate_id


class NewsCategory(models.Model):
    """
    News article categories - separate table for flexible category management
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=7, null=True, blank=True)  # Hex color for UI
    icon = models.CharField(max_length=50, null=True, blank=True)  # Icon name
    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'news_categories'
        ordering = ['display_order', 'name']
        verbose_name_plural = 'News Categories'

    def __str__(self):
        return self.name


class NewsCategoryTranslation(models.Model):
    """
    Translations for NewsCategory name and description.
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    category = models.ForeignKey(
        NewsCategory,
        on_delete=models.CASCADE,
        related_name='translations'
    )
    lang = models.CharField(max_length=10, db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'news_category_translations'
        unique_together = [['category', 'lang']]

    def __str__(self):
        return f"{self.category.name} ({self.lang})"


class Priority(models.TextChoices):
    """Article priority levels."""
    CRITICAL = 'CRITICAL', 'Critical'
    HIGH = 'HIGH', 'High'
    NORMAL = 'NORMAL', 'Normal'
    LOW = 'LOW', 'Low'


class TranslationStatus(models.TextChoices):
    """Translation status."""
    DRAFT = 'DRAFT', 'Draft'
    REVIEWED = 'REVIEWED', 'Reviewed'
    PUBLISHED = 'PUBLISHED', 'Published'
    REJECTED = 'REJECTED', 'Rejected'


class IngestionStatus(models.TextChoices):
    """Article ingestion pipeline status."""
    INGESTED    = 'INGESTED',    'Ingested'     # 入庫，尚未處理
    PROCESSED   = 'PROCESSED',  'Processed'    # quality >= 30，entity/categorize 完成
    PUBLISHED   = 'PUBLISHED',  'Published'    # quality >= 50，翻譯已排入
    LOW_QUALITY = 'LOW_QUALITY', 'Low Quality' # quality < 30，保留不公開
    DUPLICATE   = 'DUPLICATE',  'Duplicate'    # SimHash 近似重複，存 reference


class Source(models.Model):
    """RSS feed source."""
    id = models.CharField(max_length=32, primary_key=True, default=generate_id)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    feed_url = models.URLField(max_length=500)
    lang = models.CharField(max_length=10, default='en')
    priority = models.IntegerField(default=50)  # 0-100
    fetch_interval = models.IntegerField(
        default=300,
        help_text=(
            "⚠️ Read-only / legacy field. The actual fetch interval is controlled by the "
            "Celery Beat schedule defined in apps/workers/celery.py (fetch-tier-high/medium/low). "
            "Editing this field has no effect on scheduling."
        ),
    )
    is_active = models.BooleanField(default=True)

    # Health tracking (managed by fetch pipeline, not admin-editable)
    last_fetched_at = models.DateTimeField(null=True, blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    consecutive_errors = models.IntegerField(default=0)
    is_healthy = models.BooleanField(default=True, db_index=True)
    total_articles_fetched = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sources'
        ordering = ['-priority']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Content tag for articles."""
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tags'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    """
    News article - main content entity with multilingual support.
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    external_id = models.CharField(max_length=325, unique=True, db_index=True, null=True, blank=True)
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        related_name='articles'
    )

    # Original content
    original_lang = models.CharField(max_length=10)
    original_title = models.CharField(max_length=500)
    original_slug = models.SlugField(max_length=200, db_index=True)
    original_body = models.TextField()
    original_summary = models.TextField(null=True, blank=True)
    original_url = models.URLField(max_length=1000)
    simhash = models.CharField(max_length=64, null=True, blank=True, db_index=True, help_text="64-bit SimHash fingerprint for deduplication")

    # Metadata
    author = models.CharField(max_length=200, null=True, blank=True)
    published_at = models.DateTimeField(db_index=True)
    fetched_at = models.DateTimeField(auto_now_add=True)

    # Media
    featured_image_url = models.URLField(max_length=1000, null=True, blank=True)
    thumbnail_url = models.URLField(max_length=1000, null=True, blank=True)

    # Classification
    categories = models.ManyToManyField(
        NewsCategory,
        through='ArticleCategory',
        related_name='articles'
    )
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL, db_index=True)

    # Relations to F1 entities
    drivers = models.ManyToManyField(
        'teams.Driver',
        through='ArticleDriver',
        related_name='news_articles',
        blank=True
    )
    teams = models.ManyToManyField(
        'teams.Team',
        through='ArticleTeam',
        related_name='news_articles',
        blank=True
    )
    circuits = models.ManyToManyField(
        'circuits.Circuit',
        through='ArticleCircuit',
        related_name='news_articles',
        blank=True
    )
    races = models.ManyToManyField(
        'racing.Race',
        through='ArticleRace',
        related_name='news_articles',
        blank=True
    )
    tags = models.ManyToManyField(
        Tag,
        through='ArticleTag',
        related_name='articles',
        blank=True
    )

    # Status
    ingestion_status = models.CharField(
        max_length=20,
        choices=IngestionStatus.choices,
        default=IngestionStatus.INGESTED,
        db_index=True,
    )
    # DEPRECATED: Use is_visible instead.
    # is_published alone does not reflect pipeline approval state; pairing it with
    # ingestion_status as two separate gates creates a dual truth source.
    # Keep this field for manual editorial override (e.g. unpublish a live article).
    is_published = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_duplicate = models.BooleanField(default=False, db_index=True, help_text="Is this a duplicate of another article?")
    quality_score = models.FloatField(default=0.0, db_index=True, help_text="Content quality score 0.0-100.0")
    view_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'articles'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at', 'is_published']),
            models.Index(fields=['source', '-published_at']),
            models.Index(fields=['priority', '-published_at']),
        ]

    def __str__(self):
        return self.original_title

    @property
    def is_visible(self) -> bool:
        """Single source of truth for public visibility.

        An article is visible iff it has cleared the ingestion pipeline
        (ingestion_status == PUBLISHED) *and* has not been manually suppressed
        (is_published == True).  Prefer this over checking either field alone.
        """
        return self.ingestion_status == IngestionStatus.PUBLISHED and self.is_published

    def save(self, *args, **kwargs):
        if not self.original_slug:
            self.original_slug = slugify(self.original_title)
        super().save(*args, **kwargs)


class ChunkType(models.TextChoices):
    """Type of content chunk."""
    HEADING = 'HEADING', 'Heading'
    PARAGRAPH = 'PARAGRAPH', 'Paragraph'
    LIST = 'LIST', 'List'
    QUOTE = 'QUOTE', 'Quote'
    IMAGE = 'IMAGE', 'Image'
    OTHER = 'OTHER', 'Other'


class ArticleChunk(models.Model):
    """
    Segmented content of an article for AI processing and granular access.
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    sequence = models.IntegerField(help_text="Order of the chunk in the article")
    content = models.TextField()
    chunk_type = models.CharField(
        max_length=20,
        choices=ChunkType.choices,
        default=ChunkType.PARAGRAPH
    )
    
    # Future-proofing for vector search
    # embedding = VectorField()  # To be added when pgvector is integrated

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'article_chunks'
        ordering = ['sequence']
        indexes = [
            models.Index(fields=['article', 'sequence']),
        ]

    def __str__(self):
        return f"{self.article.original_title} - Chunk {self.sequence}"


class Translation(models.Model):
    """
    Article translation - supports multiple languages per article.
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='translations'
    )

    # Translation content
    lang = models.CharField(max_length=10, db_index=True)  # ISO 639-1 language code
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=200, db_index=True)
    body = models.TextField()
    summary = models.TextField(null=True, blank=True)

    # Quality control
    status = models.CharField(
        max_length=20,
        choices=TranslationStatus.choices,
        default=TranslationStatus.DRAFT,
        db_index=True
    )
    confidence_score = models.FloatField(default=0.0)  # AI confidence score 0.0-1.0
    translator = models.CharField(max_length=100, null=True, blank=True)  # AI model or human translator

    # Timestamps
    translated_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'translations'
        unique_together = [['article', 'lang']]
        ordering = ['article', 'lang']
        indexes = [
            models.Index(fields=['lang', 'status']),
            models.Index(fields=['slug', 'lang']),
            models.Index(fields=['article', 'lang']),
        ]

    def __str__(self):
        return f"{self.title} ({self.lang})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


# Junction tables for Article relationships

class ArticleCategory(models.Model):
    """Article-Category relationship."""
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)  # One category can be marked as primary

    class Meta:
        db_table = 'article_categories'
        unique_together = [['article', 'category']]
        indexes = [
            models.Index(fields=['article', 'is_primary']),
        ]

    def __str__(self):
        return f"{self.article.original_title} - {self.category.name}"


class ArticleDriver(models.Model):
    """Article-Driver relationship."""
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    driver = models.ForeignKey('teams.Driver', on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)  # Main driver mentioned in article

    class Meta:
        db_table = 'article_drivers'
        unique_together = [['article', 'driver']]

    def __str__(self):
        return f"{self.article.original_title} - {self.driver.full_name}"


class ArticleTeam(models.Model):
    """Article-Team relationship."""
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)  # Main team mentioned in article

    class Meta:
        db_table = 'article_teams'
        unique_together = [['article', 'team']]

    def __str__(self):
        return f"{self.article.original_title} - {self.team.base_name}"


class ArticleCircuit(models.Model):
    """Article-Circuit relationship."""
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    circuit = models.ForeignKey('circuits.Circuit', on_delete=models.CASCADE)

    class Meta:
        db_table = 'article_circuits'
        unique_together = [['article', 'circuit']]

    def __str__(self):
        return f"{self.article.original_title} - {self.circuit.name}"


class ArticleRace(models.Model):
    """Article-Race relationship."""
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    race = models.ForeignKey('racing.Race', on_delete=models.CASCADE)

    class Meta:
        db_table = 'article_races'
        unique_together = [['article', 'race']]

    def __str__(self):
        return f"{self.article.original_title} - {self.race.official_name}"


class ArticleTag(models.Model):
    """Article-Tag relationship."""
    id = models.CharField(max_length=32, primary_key=True, default=generate_id, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        db_table = 'article_tags'
        unique_together = [['article', 'tag']]

    def __str__(self):
        return f"{self.article.original_title} - {self.tag.name}"
