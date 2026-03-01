#!/bin/sh
set -e

# Determine process type from first argument.
# Only the API process (gunicorn) needs to run migrations;
# worker and beat containers skip this to avoid race conditions and noise.
PROCESS_TYPE="${1:-gunicorn}"

if [ "$PROCESS_TYPE" = "gunicorn" ]; then
  echo "Running database migrations..."
  python manage.py migrate --run-syncdb
  echo "Collecting static files..."
  python manage.py collectstatic --noinput --clear 2>/dev/null || true
fi

echo "Starting $PROCESS_TYPE..."
exec "$@"
