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

# Collect static files at build time (uses fallback SECRET_KEY from base settings)
RUN DJANGO_SETTINGS_MODULE=config.settings.base \
    python manage.py collectstatic --noinput --clear

# Make scripts executable
RUN chmod +x manage.py entrypoint.sh

EXPOSE 8000

# APP_ROLE: api (default) | worker | beat
CMD ["./entrypoint.sh"]
