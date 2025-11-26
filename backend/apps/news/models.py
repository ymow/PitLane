"""News app models."""
from django.db import models
from django.utils.text import slugify
import uuid


def generate_id():
    """Generate a short unique ID."""
    return uuid.uuid4().hex[:25]


class Category(models.TextChoices):
    """Article categories."""
    BREAKING = 'BREAKING', 'Breaking News'
    NEWS = 'NEWS', 'General News'
    RACE_REPORT = 'RACE_REPORT', 'Race Report'
    QUALIFYING = 'QUALIFYING', 'Qualifying'
    PRACTICE = 'PRACTICE', 'Practice'
    TECHNICAL = 'TECHNICAL', 'Technical'
    TRANSFER = 'TRANSFER', 'Transfer News'
    OPINION = 'OPINION', 'Opinion'


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


class Source(models.Model):
    """RSS feed source."""
    id = models.CharField(max_length=25, primary_key=True, default=generate_id)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    feed_url = models.URLField(max_length=500)
    lang = models.CharField(max_length=10, default='en')
    priority = models.IntegerField(default=50)  # 0-100
    fetch_interval = models.IntegerField(default=300)  # seconds
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sources'
        ordering = ['-priority']

    def __str__(self):
        return self.name


class Team(models.Model):
    """F1 Team."""
    id = models.CharField(max_length=25, primary_key=True, default=generate_id)
    code = models.CharField(max_length=10, unique=True)  # RBR, MCL, FER
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    primary_color = models.CharField(max_length=7, null=True, blank=True)  # #FF8000
    logo_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teams'

    def __str__(self):
        return self.name


class Driver(models.Model):
    """F1 Driver."""
    id = models.CharField(max_length=25, primary_key=True, default=generate_id)
    code = models.CharField(max_length=3, unique=True)  # VER, NOR, HAM
    number = models.IntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nationality = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='drivers')
    image_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'drivers'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Tag(models.Model):
    """Content tag."""
    id = models.CharField(max_length=25, primary_key=True, default=generate_id)
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tags'

    def __str__(self):
        return self.name


class Article(models.Model):
    """News article."""
    id = models.CharField(max_length=25, primary_key=True, default=generate_id)
    external_id = models.CharField(max_length=64, unique=True, db_index=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='articles')

    # Original content
    original_lang = models.CharField(max_length=10)
    original_title = models.CharField(max_length=500)
    original_slug = models.SlugField(max_length=200, db_index=True)
    original_body = models.TextField()
    original_url = models.URLField(max_length=1000)

    # Metadata
    published_at = models.DateTimeField(db_index=True)
    fetched_at = models.DateTimeField()
    image_url = models.URLField(max_length=1000, null=True, blank=True)

    # Classification
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.NEWS)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL)

    # Relations
    drivers = models.ManyToManyField(Driver, through='ArticleDriver', related_name='articles')
    teams = models.ManyToManyField(Team, through='ArticleTeam', related_name='articles')
    tags = models.ManyToManyField(Tag, through='ArticleTag', related_name='articles')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'articles'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['category', '-published_at']),
            models.Index(fields=['source', '-published_at']),
        ]

    def __str__(self):
        return self.original_title

    def save(self, *args, **kwargs):
        if not self.original_slug:
            self.original_slug = slugify(self.original_title)
        super().save(*args, **kwargs)


class Translation(models.Model):
    """Article translation."""
    id = models.CharField(max_length=25, primary_key=True, default=generate_id)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='translations')

    lang = models.CharField(max_length=10)
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=200)
    body = models.TextField()
    summary = models.TextField(null=True, blank=True)

    # Quality control
    status = models.CharField(max_length=20, choices=TranslationStatus.choices, default=TranslationStatus.DRAFT)
    confidence = models.FloatField(default=0.0)  # AI confidence score
    translated_at = models.DateTimeField()
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'translations'
        unique_together = [['article', 'lang']]
        indexes = [
            models.Index(fields=['lang', 'status']),
            models.Index(fields=['slug', 'lang']),
        ]

    def __str__(self):
        return f"{self.title} ({self.lang})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


# Junction tables
class ArticleDriver(models.Model):
    """Article-Driver relationship."""
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)

    class Meta:
        db_table = 'article_drivers'
        unique_together = [['article', 'driver']]


class ArticleTeam(models.Model):
    """Article-Team relationship."""
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        db_table = 'article_teams'
        unique_together = [['article', 'team']]


class ArticleTag(models.Model):
    """Article-Tag relationship."""
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        db_table = 'article_tags'
        unique_together = [['article', 'tag']]
