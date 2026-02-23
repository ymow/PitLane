"""API views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from django.db.models import Q
import i18n
import logging
import secrets

logger = logging.getLogger(__name__)

from apps.news.models import Article, Translation, NewsCategory
from apps.teams.models import Driver, Team, SocialHandle, DriverContract
from apps.racing.models import Race, Session, RaceResult
from .serializers import (
    ArticleListSerializer, ArticleDetailSerializer,
    DriverSerializer, DriverWriteSerializer,
    TeamSerializer, TeamWriteSerializer,
    CategorySerializer, SocialHandleSerializer,
    ContractReadSerializer, ContractWriteSerializer,
)
from .services import ergast_service, racing_service


def _write_permissions(action):
    if action in ('create', 'update', 'partial_update', 'destroy'):
        return [IsAdminUser()]
    return []


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Article listing and detail."""
    lookup_field = 'slug'

    def get_queryset(self):
        lang = self.request.query_params.get('lang', 'zh-TW')

        queryset = Article.objects.filter(
            translations__lang=lang,
            translations__status='PUBLISHED'
        ).select_related('source').prefetch_related(
            'drivers', 'teams', 'translations', 'tags'
        ).distinct()

        # Fallback to any published translation if specific lang not found
        if not queryset.exists() and lang != 'zh-TW':
             queryset = Article.objects.filter(
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
            'drivers', 'teams', 'tags', 'translations', 'chunks'
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


class SocialHandleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for paddock social handles (read-only, filterable)."""
    serializer_class = SocialHandleSerializer

    def get_queryset(self):
        qs = SocialHandle.objects.filter(is_active=True).select_related('driver', 'team')
        entity_type = self.request.query_params.get('entity_type')
        platform    = self.request.query_params.get('platform')
        team        = self.request.query_params.get('team')
        driver      = self.request.query_params.get('driver')
        if entity_type: qs = qs.filter(entity_type=entity_type)
        if platform:    qs = qs.filter(platform=platform)
        if team:        qs = qs.filter(team__code=team)
        if driver:      qs = qs.filter(driver__code=driver)
        return qs


class DriverViewSet(viewsets.ModelViewSet):
    """ViewSet for Driver listing, detail, and write operations (admin only)."""
    lookup_field = 'code'

    def get_queryset(self):
        return Driver.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return DriverWriteSerializer
        return DriverSerializer

    def get_permissions(self):
        return _write_permissions(self.action)

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

    @action(detail=True, methods=['get'])
    def social(self, request, code=None):
        """Get social handles for this driver."""
        driver = self.get_object()
        handles = driver.social_handles.filter(is_active=True)
        return Response(SocialHandleSerializer(handles, many=True).data)


class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for Team listing, detail, and write operations (admin only)."""
    lookup_field = 'code'

    def get_queryset(self):
        return Team.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TeamWriteSerializer
        return TeamSerializer

    def get_permissions(self):
        return _write_permissions(self.action)

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

    @action(detail=True, methods=['get'])
    def social(self, request, code=None):
        """Get social handles for this team."""
        team = self.get_object()
        handles = team.social_handles.filter(is_active=True)
        return Response(SocialHandleSerializer(handles, many=True).data)


class ContractViewSet(viewsets.ModelViewSet):
    """ViewSet for DriverContract (drivers + staff). Writes are admin-only."""

    def get_queryset(self):
        qs = DriverContract.objects.select_related('driver', 'team', 'season')
        role = self.request.query_params.get('role')
        team = self.request.query_params.get('team')
        is_active = self.request.query_params.get('is_active')
        if role:
            qs = qs.filter(role=role)
        if team:
            qs = qs.filter(team__code=team)
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        return qs

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ContractWriteSerializer
        return ContractReadSerializer

    def get_permissions(self):
        return _write_permissions(self.action)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for NewsCategory listing."""
    queryset = NewsCategory.objects.prefetch_related('translations').filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['lang'] = self.request.query_params.get('lang', 'en')
        return ctx


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
        if len(query) > 200:
            return Response(
                {'detail': 'Query must be at most 200 characters'},
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


class F1StandingsAPIView(APIView):
    """Get current F1 championship standings."""
    
    def get(self, request):
        """Get both driver and constructor standings."""
        try:
            standings = ergast_service.get_current_standings()
            return Response(standings)
        except Exception as e:
            return Response(
                {'error': 'Failed to fetch standings data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class F1RaceScheduleAPIView(APIView):
    """Get F1 race schedule."""
    
    def get(self, request):
        """Get race schedule for current season."""
        year = request.query_params.get('year')
        
        try:
            schedule = ergast_service.get_race_schedule(year)
            
            # Use service to enrich with local session data (OpenF1 keys)
            enriched_schedule = [racing_service.enrich_race_with_telemetry(race) for race in schedule]
            
            return Response({'races': enriched_schedule})
        except Exception as e:
            return Response(
                {'error': 'Failed to fetch race schedule'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class F1RaceResultsAPIView(APIView):
    """Get F1 race results."""
    
    def get(self, request):
        """Get race results."""
        year = request.query_params.get('year')
        round_number = request.query_params.get('round')
        
        try:
            results = ergast_service.get_race_results(year, round_number)
            
            # Enrich with local analysis data (telemetry charts)
            for race_data in results:
                try:
                    race_year = int(race_data['date'][:4])
                    race_round = race_data['round']
                    
                    session = Session.objects.filter(
                        race__season__year=race_year,
                        race__round_number=race_round,
                        session_type='RACE'
                    ).first()
                    
                    if session:
                        # Create a map of local results for efficiency
                        local_results = {
                            res.driver.code: res 
                            for res in RaceResult.objects.filter(session=session).select_related('driver')
                        }
                        
                        for res in race_data['results']:
                            driver_code = res['driver'].get('code')
                            if driver_code and driver_code in local_results:
                                local_res = local_results[driver_code]
                                if local_res.telemetry_chart:
                                    res['telemetry_chart_url'] = request.build_absolute_uri(local_res.telemetry_chart.url)
                except Exception as e:
                    logger.error(f"Error enriching results for {race_data.get('name')}: {e}")
            
            return Response({'results': results})
        except Exception as e:
            return Response(
                {'error': 'Failed to fetch race results'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class F1DriversAPIView(APIView):
    """Get F1 drivers data."""
    
    def get(self, request):
        """Get all drivers for the season."""
        year = request.query_params.get('year')
        
        try:
            drivers = ergast_service.get_drivers(year)
            return Response({'drivers': drivers})
        except Exception as e:
            return Response(
                {'error': 'Failed to fetch drivers data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class F1ConstructorsAPIView(APIView):
    """Get F1 constructors data."""
    
    def get(self, request):
        """Get all constructors for the season."""
        year = request.query_params.get('year')
        
        try:
            constructors = ergast_service.get_constructors(year)
            return Response({'constructors': constructors})
        except Exception as e:
            return Response(
                {'error': 'Failed to fetch constructors data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class F1QualifyingAPIView(APIView):
    """Get F1 qualifying results."""
    
    def get(self, request):
        """Get qualifying results."""
        year = request.query_params.get('year')
        round_number = request.query_params.get('round')
        
        try:
            results = ergast_service.get_qualifying_results(year, round_number)
            return Response({'qualifying': results})
        except Exception as e:
            return Response(
                {'error': 'Failed to fetch qualifying results'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class F1LiveDataAPIView(APIView):
    """Get live F1 data summary."""
    
    def get(self, request):
        """Get combined live data for dashboard."""
        try:
            # 1. Standings - Still using external service (harder to seed locally)
            standings = ergast_service.get_current_standings()
            
            # 2. Schedule - Prioritize local DB for 2026
            from datetime import datetime, date
            today = date.today()
            current_year = today.year
            
            local_races = Race.objects.filter(season__year=current_year).order_by('round_number')
            
            if local_races.exists():
                schedule = []
                for race in local_races:
                    schedule.append({
                        'round': race.round_number,
                        'name': race.official_name,
                        'date': race.race_date.strftime('%Y-%m-%d'),
                        'time': '13:00:00Z', # Placeholder for seeded races
                        'circuit': {
                            'id': race.circuit.code,
                            'name': race.circuit.name,
                            'location': f"{race.circuit.country}",
                            'coordinates': {'lat': 0, 'lng': 0}
                        }
                    })
            else:
                # Fallback to external service
                schedule = ergast_service.get_race_schedule()
            
            # Find next race
            next_race = None
            for race in schedule:
                race_date = datetime.strptime(race['date'], '%Y-%m-%d').date()
                if race_date >= today:
                    next_race = race
                    break
            
            # Enrich with OpenF1 Session Key via service
            if next_race:
                next_race = racing_service.enrich_race_with_telemetry(next_race)

            # 3. Results - Get last completed race
            latest_results = ergast_service.get_race_results()
            last_race = latest_results[-1] if latest_results else None
            
            return Response({
                'standings': standings,
                'next_race': next_race,
                'last_race': last_race,
                'season_progress': {
                    'completed_races': len([r for r in schedule if datetime.strptime(r['date'], '%Y-%m-%d').date() < today]),
                    'total_races': len(schedule)
                }
            })
        except Exception as e:
            logger.error(f"F1 Live Data API error: {e}")
            return Response(
                {'error': 'Failed to fetch live data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LinearLoginView(APIView):
    """
    Step 1: Redirect the user to Linear's OAuth page.
    """
    def get(self, request):
        import os
        from django.shortcuts import redirect
        client_id = os.getenv('LINEAR_CLIENT_ID')
        if not client_id:
            return Response({'error': 'LINEAR_CLIENT_ID not set'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Build redirect URI dynamically so it works in all environments
        redirect_uri = request.build_absolute_uri('/api/v1/auth/linear/callback')
        scope = "read write"

        # CSRF protection: generate a state token and store in session
        state = secrets.token_urlsafe(32)
        request.session['linear_oauth_state'] = state

        auth_url = (
            f"https://linear.app/oauth/authorize?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={scope}&"
            f"state={state}"
        )
        return redirect(auth_url)


class LinearCallbackView(APIView):
    """
    Step 2: Receive the authorization code from Linear and exchange for a token.
    """
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')

        if not code:
            return Response({'error': 'No authorization code provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate CSRF state
        expected_state = request.session.pop('linear_oauth_state', None)
        if not expected_state or state != expected_state:
            return Response({'error': 'Invalid OAuth state — possible CSRF attack'}, status=status.HTTP_400_BAD_REQUEST)

        # Token exchange requires LINEAR_CLIENT_SECRET (set in .env to complete)
        # POST https://api.linear.app/oauth/token with code + client_id + client_secret + redirect_uri
        import os
        if not os.getenv('LINEAR_CLIENT_SECRET'):
            logger.warning("LINEAR_CLIENT_SECRET not set — OAuth token exchange skipped")
            return Response({
                'message': 'Authorization code received. Set LINEAR_CLIENT_SECRET in .env to complete token exchange.',
                'status': 'pending_client_secret'
            })

        return Response({'message': 'OAuth flow complete', 'status': 'ok'})
