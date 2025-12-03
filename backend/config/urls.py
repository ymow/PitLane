"""URL configuration for PitLane project."""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        'message': 'PitLane F1 News API',
        'version': 'v1',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/v1/',
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.api.urls')),
]
