"""Celery configuration for PitLane."""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('pitlane')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Task routing
app.conf.task_routes = {
    'apps.workers.tasks.fetch.*': {'queue': 'fetch'},
    'apps.workers.tasks.translate.*': {'queue': 'translate'},
    'apps.workers.tasks.process.*': {'queue': 'process'},
}

# Rate limits
app.conf.task_annotations = {
    'apps.workers.tasks.translate.translate_article': {
        'rate_limit': '10/m',  # Claude API rate limit
    },
}

# Celery Beat Schedule
app.conf.beat_schedule = {
    # High priority sources: every 5 minutes
    'fetch-high-priority': {
        'task': 'apps.workers.tasks.fetch.fetch_sources_by_priority',
        'schedule': crontab(minute='*/5'),
        'args': (['fia-press', 'motorsport', 'the-race', 'autosport'],),
    },

    # Medium priority: every 15 minutes
    'fetch-medium-priority': {
        'task': 'apps.workers.tasks.fetch.fetch_sources_by_priority',
        'schedule': crontab(minute='*/15'),
        'args': (['racefans', 'f1i'],),
    },

    # Low priority (EN): every 30 minutes
    'fetch-low-priority': {
        'task': 'apps.workers.tasks.fetch.fetch_sources_by_priority',
        'schedule': crontab(minute='*/30'),
        'args': (['formel1-de', 'motorsport-it'],),
    },

    # European/Japanese markets: every 30 minutes
    'fetch-international': {
        'task': 'apps.workers.tasks.fetch.fetch_sources_by_priority',
        'schedule': crontab(minute='*/30'),
        'args': ([
            'motorsport-total',                      # de
            'f1grandprix-it',                        # it
            'motorsport-es', 'f1latam',              # es
            'motorsport-br', 'autoracing',           # pt-BR
            'headliner-nl', 'motorsport-nl',         # nl
            'motorsport-fr', 'f1only',               # fr
            'motorsport-jp',                         # ja
            'motorsport-tr', 'trf1',                 # tr
            'motorsport-pl',                         # pl
        ],),
    },

    # Cache warmup: every hour
    'warm-cache': {
        'task': 'apps.workers.tasks.process.warm_cache',
        'schedule': crontab(minute=0),
    },

    # Cleanup old articles: daily at 3 AM
    'cleanup-old-articles': {
        'task': 'apps.workers.tasks.process.cleanup_old_articles',
        'schedule': crontab(hour=3, minute=0),
        'args': (90,),  # Keep 90 days
    },
}


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing."""
    print(f'Request: {self.request!r}')
