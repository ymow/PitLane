"""API serializers."""
from rest_framework import serializers
from apps.news.models import Article, Translation, Source, Tag, NewsCategory
from apps.teams.models import Driver, Team, SocialHandle, DriverContract


class SourceSerializer(serializers.ModelSerializer):
    """Source serializer."""
    class Meta:
        model = Source
        fields = ['id', 'name', 'slug']


class TeamSerializer(serializers.ModelSerializer):
    """Team serializer."""
    class Meta:
        model = Team
        fields = ['id', 'code', 'base_name', 'primary_color', 'logo_url']


class DriverSerializer(serializers.ModelSerializer):
    """Driver serializer."""
    class Meta:
        model = Driver
        fields = ['id', 'code', 'racing_number', 'first_name', 'last_name', 'full_name', 'nationality', 'headshot_url']


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer."""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class CategorySerializer(serializers.ModelSerializer):
    """News category with translation support."""
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = NewsCategory
        fields = ['id', 'name', 'slug', 'display_name', 'color', 'icon']

    def get_display_name(self, obj):
        """Get translated category name."""
        lang = self.context.get('lang', 'en')
        translation = obj.translations.filter(lang=lang).first()
        return translation.name if translation else obj.name


class SocialHandleSerializer(serializers.ModelSerializer):
    driver_name = serializers.SerializerMethodField()
    team_name   = serializers.SerializerMethodField()

    class Meta:
        model = SocialHandle
        fields = ['id', 'platform', 'handle', 'url', 'entity_type',
                  'driver_name', 'team_name', 'staff_name', 'role',
                  'is_verified', 'follower_count']

    def get_driver_name(self, obj):
        return obj.driver.full_name if obj.driver else None

    def get_team_name(self, obj):
        return obj.team.base_name if obj.team else None


class TeamWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['code', 'base_name', 'country', 'headquarters', 'founded_year',
                  'primary_color', 'secondary_color', 'logo_url', 'website', 'is_active']


class DriverWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['code', 'first_name', 'last_name', 'full_name', 'nationality',
                  'date_of_birth', 'place_of_birth', 'racing_number',
                  'headshot_url', 'profile_image_url', 'status', 'is_active']


class ContractWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DriverContract
        fields = ['driver', 'team', 'season', 'role', 'person_name',
                  'car_number', 'is_active', 'valid_from', 'valid_until',
                  'announcement_date', 'notes']

    def validate(self, data):
        driver_roles = {'RACE', 'RESERVE', 'TEST', 'DEVELOPMENT', 'LOAN', 'GUEST'}
        if data.get('role') in driver_roles and not data.get('driver'):
            raise serializers.ValidationError("Driver roles require a linked driver.")
        if data.get('role') not in driver_roles and not data.get('person_name'):
            raise serializers.ValidationError("Staff roles require person_name.")
        return data


class ContractReadSerializer(serializers.ModelSerializer):
    driver_name   = serializers.SerializerMethodField()
    team_code     = serializers.CharField(source='team.code', read_only=True)
    primary_color = serializers.CharField(source='team.primary_color', read_only=True)
    season_year   = serializers.IntegerField(source='season.year', read_only=True)

    class Meta:
        model  = DriverContract
        fields = ['id', 'driver', 'driver_name', 'person_name', 'team', 'team_code',
                  'primary_color', 'season', 'season_year', 'role', 'car_number',
                  'is_active', 'valid_from', 'valid_until', 'announcement_date', 'notes']

    def get_driver_name(self, obj):
        return obj.driver.full_name if obj.driver else None


class ArticleChunkSerializer(serializers.Serializer):
    """Serializer for article content chunks."""
    sequence = serializers.IntegerField()
    content = serializers.CharField()
    chunk_type = serializers.CharField()


class ArticleDriverSerializer(serializers.Serializer):
    """Driver with primary status."""
    id = serializers.ReadOnlyField(source='driver.id')
    code = serializers.ReadOnlyField(source='driver.code')
    first_name = serializers.ReadOnlyField(source='driver.first_name')
    last_name = serializers.ReadOnlyField(source='driver.last_name')
    full_name = serializers.ReadOnlyField(source='driver.full_name')
    headshot_url = serializers.ReadOnlyField(source='driver.headshot_url')
    is_primary = serializers.BooleanField()


class ArticleTeamSerializer(serializers.Serializer):
    """Team with primary status."""
    id = serializers.ReadOnlyField(source='team.id')
    code = serializers.ReadOnlyField(source='team.code')
    base_name = serializers.ReadOnlyField(source='team.base_name')
    primary_color = serializers.ReadOnlyField(source='team.primary_color')
    logo_url = serializers.ReadOnlyField(source='team.logo_url')
    is_primary = serializers.BooleanField()


class ArticleListSerializer(serializers.Serializer):
    """Article list serializer with translation support."""
    id = serializers.CharField()
    title = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    image_url = serializers.URLField(source='featured_image_url', allow_null=True)
    published_at = serializers.DateTimeField()
    category = serializers.SerializerMethodField()
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
        return translation.summary if translation else obj.original_summary

    def get_category(self, obj):
        """Get primary category details."""
        primary_category = obj.categories.filter(
            articlecategory__is_primary=True
        ).first() or obj.categories.first()

        if primary_category:
            return CategorySerializer(primary_category, context=self.context).data
        return None

    def get_drivers(self, obj):
        """Get drivers with minimal info."""
        relations = obj.articledriver_set.all()[:3]
        return [
            {
                'code': r.driver.code,
                'last_name': r.driver.last_name,
                'is_primary': r.is_primary
            }
            for r in relations
        ]

    def get_teams(self, obj):
        """Get teams with minimal info."""
        relations = obj.articleteam_set.all()[:3]
        return [
            {
                'code': r.team.code,
                'base_name': r.team.base_name,
                'is_primary': r.is_primary
            }
            for r in relations
        ]


class ArticleDetailSerializer(serializers.Serializer):
    """Article detail serializer with full content and chunks."""
    id = serializers.CharField()
    title = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()
    chunks = ArticleChunkSerializer(many=True, read_only=True)
    image_url = serializers.URLField(source='featured_image_url', allow_null=True)
    published_at = serializers.DateTimeField()
    category = serializers.SerializerMethodField()
    priority = serializers.CharField()
    original_url = serializers.URLField()
    source = SourceSerializer()
    drivers = ArticleDriverSerializer(source='articledriver_set', many=True, read_only=True)
    teams = ArticleTeamSerializer(source='articleteam_set', many=True, read_only=True)
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
        return translation.summary if translation else obj.original_summary

    def get_body(self, obj):
        """Get translated body."""
        lang = self.context.get('lang', 'en')
        translation = obj.translations.filter(lang=lang, status='PUBLISHED').first()
        return translation.body if translation else obj.original_body

    def get_category(self, obj):
        """Get primary category details."""
        primary_category = obj.categories.filter(
            articlecategory__is_primary=True
        ).first() or obj.categories.first()
        
        if primary_category:
            return CategorySerializer(primary_category, context=self.context).data
        return None
