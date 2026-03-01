#!/bin/bash
set -e

APP_ROLE="${APP_ROLE:-api}"

case "$APP_ROLE" in
  api)
    echo "Running migrations..."
    python manage.py migrate --noinput

    echo "Starting gunicorn [workers=${GUNICORN_WORKERS:-4}]..."
    exec gunicorn config.wsgi:application \
      --bind "0.0.0.0:${PORT:-8000}" \
      --workers "${GUNICORN_WORKERS:-4}" \
      --timeout "${GUNICORN_TIMEOUT:-120}" \
      --log-level info \
      --access-logfile -
    ;;

  worker)
    echo "Starting Celery worker [queues=${CELERY_QUEUES:-fetch,translate,process,celery}]..."
    exec celery -A apps.workers.celery worker \
      --loglevel="${CELERY_LOG_LEVEL:-info}" \
      --queues="${CELERY_QUEUES:-fetch,translate,process,celery}" \
      --concurrency="${CELERY_CONCURRENCY:-4}"
    ;;

  beat)
    echo "Starting Celery beat..."
    exec celery -A apps.workers.celery beat \
      --loglevel="${CELERY_LOG_LEVEL:-info}" \
      --schedule /tmp/celerybeat-schedule
    ;;

  *)
    echo "ERROR: Unknown APP_ROLE='$APP_ROLE'. Valid values: api, worker, beat" >&2
    exit 1
    ;;
esac
