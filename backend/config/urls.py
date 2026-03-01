"""URL configuration for PitLane project."""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection


def api_root(request):
    return JsonResponse({
        'message': 'PitLane F1 News API',
        'version': 'v1',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/v1/',
            'health': '/health/',
        }
    })


def health_check(request):
    """Liveness probe: verify DB is reachable."""
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False

    payload = {'status': 'ok' if db_ok else 'degraded', 'db': db_ok}
    status_code = 200 if db_ok else 503
    return JsonResponse(payload, status=status_code)


urlpatterns = [
    path('', api_root, name='api_root'),
    path('health/', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.api.urls')),
]
