"""API URLs."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, DriverViewSet, TeamViewSet, I18nView, SearchView

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'teams', TeamViewSet, basename='team')

urlpatterns = [
    path('', include(router.urls)),
    path('i18n/', I18nView.as_view(), name='i18n'),
    path('search/', SearchView.as_view(), name='search'),
]
