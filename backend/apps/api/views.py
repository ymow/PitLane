"""API views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from django.db.models import Q
import i18n

from apps.news.models import Article, Translation, Driver, Team
from .serializers import (
    ArticleListSerializer, ArticleDetailSerializer,
    DriverSerializer, TeamSerializer
)


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Article listing and detail."""
    lookup_field = 'slug'

    def get_queryset(self):
        lang = self.request.query_params.get('lang', 'en')

        queryset = Article.objects.filter(
            translations__lang=lang,
            translations__status='PUBLISHED'
        ).select_related('source').prefetch_related(
            'drivers', 'teams', 'translations', 'tags'
        ).distinct()

        # Filters
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        driver = self.request.query_params.get('driver')
        if driver:
            queryset = queryset.filter(drivers__code=driver)

        team = self.request.query_params.get('team')
        if team:
            queryset = queryset.filter(teams__code=team)

        return queryset.order_by('-published_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['lang'] = self.request.query_params.get('lang', 'en')
        return context

    def retrieve(self, request, slug=None):
        """Retrieve article by slug (translated)."""
        lang = request.query_params.get('lang', 'en')

        # Try to find by translated slug first
        try:
            translation = Translation.objects.select_related('article').get(
                slug=slug,
                lang=lang,
                status='PUBLISHED'
            )
            article = translation.article
        except Translation.DoesNotExist:
            # Fallback to original slug
            try:
                article = Article.objects.get(original_slug=slug)
            except Article.DoesNotExist:
                return Response(
                    {'detail': 'Article not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Prefetch related data
        article = Article.objects.filter(id=article.id).select_related(
            'source'
        ).prefetch_related(
            'drivers', 'teams', 'tags', 'translations'
        ).first()

        serializer = ArticleDetailSerializer(article, context={'lang': lang})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def breaking(self, request):
        """Get breaking news articles."""
        lang = request.query_params.get('lang', 'en')
        limit = min(int(request.query_params.get('limit', 5)), 10)

        # Try cache first
        cache_key = f'breaking:news:{lang}'
        cached = cache.get(cache_key)
        if cached:
            return Response({'items': cached})

        articles = self.get_queryset().filter(
            priority__in=['CRITICAL', 'HIGH']
        )[:limit]

        serializer = ArticleListSerializer(
            articles, many=True, context={'lang': lang}
        )

        # Cache for 1 minute
        cache.set(cache_key, serializer.data, 60)

        return Response({'items': serializer.data})

    @action(detail=True, methods=['get'])
    def related(self, request, slug=None):
        """Get related articles."""
        lang = request.query_params.get('lang', 'en')
        limit = min(int(request.query_params.get('limit', 5)), 10)

        article = self.get_object()

        # Find related by shared drivers/teams/category
        related = Article.objects.filter(
            Q(drivers__in=article.drivers.all()) |
            Q(teams__in=article.teams.all()) |
            Q(category=article.category),
            translations__lang=lang,
            translations__status='PUBLISHED'
        ).exclude(id=article.id).distinct()[:limit]

        serializer = ArticleListSerializer(
            related, many=True, context={'lang': lang}
        )

        return Response({'items': serializer.data})


class DriverViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Driver listing and detail."""
    queryset = Driver.objects.select_related('team').all()
    serializer_class = DriverSerializer
    lookup_field = 'code'

    @action(detail=True, methods=['get'])
    def articles(self, request, code=None):
        """Get articles mentioning this driver."""
        driver = self.get_object()
        lang = request.query_params.get('lang', 'en')

        articles = driver.articles.filter(
            translations__lang=lang,
            translations__status='PUBLISHED'
        ).select_related('source').prefetch_related(
            'drivers', 'teams', 'translations'
        ).distinct().order_by('-published_at')

        # Pagination
        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = ArticleListSerializer(
                page, many=True, context={'lang': lang}
            )
            return self.get_paginated_response(serializer.data)

        serializer = ArticleListSerializer(
            articles, many=True, context={'lang': lang}
        )
        return Response({'items': serializer.data})


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Team listing and detail."""
    queryset = Team.objects.prefetch_related('drivers').all()
    serializer_class = TeamSerializer
    lookup_field = 'code'

    @action(detail=True, methods=['get'])
    def articles(self, request, code=None):
        """Get articles mentioning this team."""
        team = self.get_object()
        lang = request.query_params.get('lang', 'en')

        articles = team.articles.filter(
            translations__lang=lang,
            translations__status='PUBLISHED'
        ).select_related('source').prefetch_related(
            'drivers', 'teams', 'translations'
        ).distinct().order_by('-published_at')

        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = ArticleListSerializer(
                page, many=True, context={'lang': lang}
            )
            return self.get_paginated_response(serializer.data)

        serializer = ArticleListSerializer(
            articles, many=True, context={'lang': lang}
        )
        return Response({'items': serializer.data})


class I18nView(APIView):
    """Get UI translations using python-i18n."""

    def get(self, request):
        lang = request.query_params.get('lang', 'en')

        # Try cache first
        cache_key = f'i18n:{lang}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        # Set locale for python-i18n
        i18n.set('locale', lang)
        i18n.set('fallback', 'en')

        # Build translations dict
        translations = {}
        keys = [
            'site.name', 'site.tagline',
            'nav.home', 'nav.news', 'nav.breaking', 'nav.drivers', 'nav.teams',
            'news.breaking', 'news.latest', 'news.read_more', 'news.published_at',
            'news.source', 'news.related_articles', 'news.no_results',
            'categories.BREAKING', 'categories.NEWS', 'categories.RACE_REPORT',
            'categories.QUALIFYING', 'categories.PRACTICE', 'categories.TECHNICAL',
            'categories.TRANSFER', 'categories.OPINION',
            'filters.all', 'filters.by_driver', 'filters.by_team', 'filters.by_category',
            'common.loading', 'common.error', 'common.retry'
        ]

        for key in keys:
            try:
                translations[key] = i18n.t(key)
            except:
                translations[key] = key  # Fallback to key itself

        result = {
            'lang': lang,
            'translations': translations
        }

        # Cache for 1 hour
        cache.set(cache_key, result, 3600)

        return Response(result)


class SearchView(APIView):
    """Full-text search for articles."""

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        lang = request.query_params.get('lang', 'en')
        limit = min(int(request.query_params.get('limit', 20)), 50)

        if len(query) < 2:
            return Response(
                {'detail': 'Query must be at least 2 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Search in translations
        articles = Article.objects.filter(
            Q(translations__title__icontains=query) |
            Q(translations__body__icontains=query),
            translations__lang=lang,
            translations__status='PUBLISHED'
        ).select_related('source').prefetch_related(
            'drivers', 'teams', 'translations'
        ).distinct().order_by('-published_at')[:limit]

        serializer = ArticleListSerializer(
            articles, many=True, context={'lang': lang}
        )

        return Response({'items': serializer.data})
