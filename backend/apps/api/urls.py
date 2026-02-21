"""API URLs."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArticleViewSet, DriverViewSet, TeamViewSet, CategoryViewSet,
    I18nView, SearchView,
    F1StandingsAPIView, F1RaceScheduleAPIView, F1RaceResultsAPIView,
    F1DriversAPIView, F1ConstructorsAPIView, F1QualifyingAPIView,
    F1LiveDataAPIView, LinearLoginView, LinearCallbackView
)

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
    path('i18n/', I18nView.as_view(), name='i18n'),
    path('search/', SearchView.as_view(), name='search'),
    
    # F1 Live Data API endpoints
    path('f1/standings/', F1StandingsAPIView.as_view(), name='f1-standings'),
    path('f1/schedule/', F1RaceScheduleAPIView.as_view(), name='f1-schedule'),
    path('f1/results/', F1RaceResultsAPIView.as_view(), name='f1-results'),
    path('f1/drivers/', F1DriversAPIView.as_view(), name='f1-drivers'),
    path('f1/constructors/', F1ConstructorsAPIView.as_view(), name='f1-constructors'),
    path('f1/qualifying/', F1QualifyingAPIView.as_view(), name='f1-qualifying'),
    path('f1/live/', F1LiveDataAPIView.as_view(), name='f1-live'),
    
    # Linear OAuth
    path('auth/linear/login/', LinearLoginView.as_view(), name='linear-login'),
    path('auth/linear/callback/', LinearCallbackView.as_view(), name='linear-callback'),
]
