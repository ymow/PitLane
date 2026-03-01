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
    # DB-driven tier fetch — sources read dynamically from DB at runtime
    # high (priority 90-100): every 5 minutes
    'fetch-tier-high': {
        'task': 'apps.workers.tasks.fetch.fetch_by_tier',
        'schedule': crontab(minute='*/5'),
        'args': ['high'],
    },

    # medium (priority 70-89): every 15 minutes
    'fetch-tier-medium': {
        'task': 'apps.workers.tasks.fetch.fetch_by_tier',
        'schedule': crontab(minute='*/15'),
        'args': ['medium'],
    },

    # low (priority 0-69): every 30 minutes
    'fetch-tier-low': {
        'task': 'apps.workers.tasks.fetch.fetch_by_tier',
        'schedule': crontab(minute='*/30'),
        'args': ['low'],
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

    # Probe unhealthy sources: every 6 hours
    'probe-unhealthy-sources': {
        'task': 'apps.workers.tasks.fetch.probe_unhealthy_sources',
        'schedule': crontab(minute=0, hour='*/6'),
    },
}


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing."""
    print(f'Request: {self.request!r}')
