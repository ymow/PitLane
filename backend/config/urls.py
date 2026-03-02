"""URL configuration for PitLane project."""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
import logging
import redis
import os

logger = logging.getLogger(__name__)


def api_root(request):
    return JsonResponse({
        'message': 'PitLane F1 News API',
        'version': 'v1',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/v1/',
        }
    })


def health(request):
    # DB check
    db_ok = False
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        logger.warning("Health check: DB connection failed", exc_info=True)

    # Redis check
    redis_ok = False
    try:
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url, socket_connect_timeout=2)
        r.ping()
        redis_ok = True
    except Exception:
        logger.warning("Health check: Redis connection failed", exc_info=True)

    status = 'ok' if (db_ok and redis_ok) else 'degraded'
    return JsonResponse({
        'status': status,
        'db': 'ok' if db_ok else 'error',
        'redis': 'ok' if redis_ok else 'error',
    }, status=200 if status == 'ok' else 503)


urlpatterns = [
    path('', api_root, name='api_root'),
    path('health/', health, name='health'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.api.urls')),
]
