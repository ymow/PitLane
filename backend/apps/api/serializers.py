"""API serializers."""
from rest_framework import serializers
from apps.news.models import Article, Translation, Driver, Team, Source, Tag


class SourceSerializer(serializers.ModelSerializer):
    """Source serializer."""
    class Meta:
        model = Source
        fields = ['id', 'name', 'slug']


class TeamSerializer(serializers.ModelSerializer):
    """Team serializer."""
    class Meta:
        model = Team
        fields = ['id', 'code', 'name', 'short_name', 'primary_color', 'logo_url']


class DriverSerializer(serializers.ModelSerializer):
    """Driver serializer."""
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Driver
        fields = ['id', 'code', 'number', 'first_name', 'last_name', 'nationality', 'team', 'image_url']


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer."""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class ArticleListSerializer(serializers.Serializer):
    """Article list serializer with translation support."""
    id = serializers.CharField()
    title = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    image_url = serializers.URLField()
    published_at = serializers.DateTimeField()
    category = serializers.CharField()
    priority = serializers.CharField()
    source = SourceSerializer()
    drivers = serializers.SerializerMethodField()
    teams = serializers.SerializerMethodField()

    class Meta:
        fields = [
            'id', 'title', 'slug', 'summary', 'image_url',
            'published_at', 'category', 'priority', 'source',
            'drivers', 'teams'
        ]

    def get_title(self, obj):
        """Get translated title."""
        lang = self.context.get('lang', 'en')
        translation = obj.translations.filter(lang=lang, status='PUBLISHED').first()
        return translation.title if translation else obj.original_title

    def get_slug(self, obj):
        """Get translated slug."""
        lang = self.context.get('lang', 'en')
        translation = obj.translations.filter(lang=lang, status='PUBLISHED').first()
        return translation.slug if translation else obj.original_slug

    def get_summary(self, obj):
        """Get translated summary."""
        lang = self.context.get('lang', 'en')
        translation = obj.translations.filter(lang=lang, status='PUBLISHED').first()
        return translation.summary if translation else None

    def get_drivers(self, obj):
        """Get drivers with minimal info."""
        return [
            {'code': d.code, 'last_name': d.last_name}
            for d in obj.drivers.all()[:3]
        ]

    def get_teams(self, obj):
        """Get teams with minimal info."""
        return [
            {'code': t.code, 'short_name': t.short_name}
            for t in obj.teams.all()[:3]
        ]


class ArticleDetailSerializer(serializers.Serializer):
    """Article detail serializer with full content."""
    id = serializers.CharField()
    title = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()
    image_url = serializers.URLField()
    published_at = serializers.DateTimeField()
    category = serializers.CharField()
    priority = serializers.CharField()
    original_url = serializers.URLField()
    source = SourceSerializer()
    drivers = DriverSerializer(many=True)
    teams = TeamSerializer(many=True)
    tags = TagSerializer(many=True)

    def get_title(self, obj):
        """Get translated title."""
        lang = self.context.get('lang', 'en')
        translation = obj.translations.filter(lang=lang, status='PUBLISHED').first()
        return translation.title if translation else obj.original_title

    def get_slug(self, obj):
        """Get translated slug."""
        lang = self.context.get('lang', 'en')
        translation = obj.translations.filter(lang=lang, status='PUBLISHED').first()
        return translation.slug if translation else obj.original_slug

    def get_summary(self, obj):
        """Get translated summary."""
        lang = self.context.get('lang', 'en')
        translation = obj.translations.filter(lang=lang, status='PUBLISHED').first()
        return translation.summary if translation else None

    def get_body(self, obj):
        """Get translated body."""
        lang = self.context.get('lang', 'en')
        translation = obj.translations.filter(lang=lang, status='PUBLISHED').first()
        return translation.body if translation else obj.original_body
