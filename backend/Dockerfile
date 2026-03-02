FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --without dev --no-root --no-interaction --no-ansi

# Copy application
COPY . .

# Make manage.py executable
RUN chmod +x manage.py

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 8000

# Default CMD: API server (gunicorn).
# Override per Zeabur service:
#   Worker: celery -A apps.workers.celery worker --loglevel=info -Q fetch,translate,process,celery
#   Beat:   celery -A apps.workers.celery beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
