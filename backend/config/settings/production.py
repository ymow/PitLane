"""Production settings."""
import os

try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    _sentry_available = True
except ImportError:
    _sentry_available = False

from .base import *  # noqa: F401,F403

DEBUG = False

# ALLOWED_HOSTS — must be explicitly set via env; no localhost fallback in production
_allowed_hosts = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(',') if h.strip()]

# WhiteNoise — serve compressed static files without a CDN
# Must sit immediately after SecurityMiddleware
_security_idx = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')  # noqa: F405
MIDDLEWARE = list(MIDDLEWARE)  # noqa: F405
MIDDLEWARE.insert(_security_idx + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database — prefer DATABASE_URL (Heroku / Railway / Render); fall back to individual vars
_database_url = os.getenv('DATABASE_URL', '')
if _database_url:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(
            _database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Individual DB_* vars from base.py; add connection pooling on top
    DATABASES['default']['CONN_MAX_AGE'] = 600  # noqa: F405
    DATABASES['default']['CONN_HEALTH_CHECKS'] = True  # noqa: F405

# Celery / Redis — enforce REDIS_URL is present; drop localhost fallback
_redis_url = os.getenv('REDIS_URL', '')
if _redis_url:
    CELERY_BROKER_URL = _redis_url
    CELERY_RESULT_BACKEND = _redis_url
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': _redis_url,
        }
    }

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000        # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# Sentry
SENTRY_DSN = os.getenv('SENTRY_DSN', '')
if SENTRY_DSN and _sentry_available:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
