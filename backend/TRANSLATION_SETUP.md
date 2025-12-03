# Translation Setup Guide

This guide explains how to enable AI-powered article translations using Claude Sonnet 4.

## Overview

PitLane uses Claude AI to automatically translate news articles into 10 supported languages:
- English (en)
- Traditional Chinese (zh-TW)
- Spanish (es)
- Brazilian Portuguese (pt-BR)
- Simplified Chinese (zh-CN)
- Italian (it)
- Dutch (nl)
- German (de)
- Japanese (ja)
- French (fr)

## How Translation Works

1. **RSS Fetch**: Articles are fetched from RSS sources every 5-30 minutes (based on source priority)
2. **Entity Extraction**: System identifies drivers, teams, and categories mentioned in the article
3. **Translation Queue**: Translation tasks are automatically queued for all supported languages
4. **AI Translation**: Claude Sonnet 4 translates the title, body, and generates a summary
5. **Quality Check**: Translations with confidence score ≥ 0.85 are auto-published; others saved as drafts
6. **Display**: Frontend automatically shows translated content based on user's language preference

## Getting Started

### 1. Get Your Anthropic API Key

1. Visit [Anthropic Console](https://console.anthropic.com/settings/keys)
2. Sign up or log in to your account
3. Navigate to **Settings** → **API Keys**
4. Click **Create Key** and copy the key (starts with `sk-ant-`)

### 2. Add API Key to .env

Open `backend/.env` and add your API key:

```bash
# Anthropic API (for AI translations)
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

**Important**: Never commit your `.env` file to version control!

### 3. Restart Celery Workers

The workers need to be restarted to pick up the new API key:

```bash
# Stop existing Celery processes
pkill -f "celery -A apps.workers.celery"

# Start Celery worker (in backend directory)
celery -A apps.workers.celery worker --loglevel=info &

# Start Celery beat scheduler (in backend directory)
celery -A apps.workers.celery beat --loglevel=info &
```

## Testing Translations

### Option 1: Manual Test via Django Shell

```bash
cd backend
python manage.py shell
```

```python
from apps.workers.tasks.translate import translate_article
from apps.news.models import Article

# Get the latest article
article = Article.objects.first()
print(f"Article: {article.original_title}")

# Queue translation to Spanish
result = translate_article.delay(article.id, 'es')
print(f"Task ID: {result.id}")

# Wait ~10 seconds, then check result
from apps.news.models import Translation
translation = Translation.objects.filter(article=article, lang='es').first()
if translation:
    print(f"Translated title: {translation.title}")
    print(f"Status: {translation.status}")
    print(f"Confidence: {translation.confidence_score}")
```

### Option 2: Wait for Automatic Translation

New articles are automatically queued for translation when fetched from RSS feeds. Check Celery worker logs:

```bash
# Worker log should show:
# [INFO] Translated <article_id> → es (confidence: 0.92)
# [INFO] Translated <article_id> → zh-TW (confidence: 0.89)
```

## Viewing Translations

### Via Django Admin

1. Navigate to http://localhost:8000/admin/
2. Go to **News** → **Translations**
3. Filter by language, status, or article

### Via API

```bash
# Get articles in Spanish
curl "http://localhost:8000/api/v1/articles/?lang=es"

# Get specific article in Traditional Chinese
curl "http://localhost:8000/api/v1/articles/article-slug/?lang=zh-TW"
```

### Via Frontend

1. Navigate to http://localhost:3000
2. Articles will display in English by default
3. When language switcher is implemented, users can select their preferred language

## Translation Statuses

| Status | Description |
|--------|-------------|
| **DRAFT** | Confidence < 0.85, needs review before publishing |
| **REVIEWED** | Manually reviewed and approved |
| **PUBLISHED** | Confidence ≥ 0.85, automatically published |
| **REJECTED** | Translation quality too low, rejected |

## Monitoring Translation Activity

### Check Celery Worker Logs

```bash
# View worker logs
tail -f /path/to/celery-worker.log

# Expected output:
# [INFO] Translated abc123 → es (confidence: 0.92)
# [INFO] Translated abc123 → zh-TW (confidence: 0.88)
# [WARNING] Translation skipped for abc123 to pt-BR - ANTHROPIC_API_KEY not configured
```

### Check Translation Stats

```bash
python manage.py shell
```

```python
from apps.news.models import Translation

# Total translations
print(f"Total: {Translation.objects.count()}")

# Published translations by language
from django.db.models import Count
stats = Translation.objects.filter(status='PUBLISHED').values('lang').annotate(count=Count('id'))
for stat in stats:
    print(f"{stat['lang']}: {stat['count']}")

# Average confidence score
from django.db.models import Avg
avg_conf = Translation.objects.aggregate(Avg('confidence_score'))
print(f"Avg confidence: {avg_conf['confidence_score__avg']:.2f}")
```

## Cost Management

Claude Sonnet 4 pricing (as of Dec 2024):
- Input: $3 per million tokens
- Output: $15 per million tokens

**Estimated costs**:
- Average article: ~2,000 tokens input, ~2,500 tokens output
- Cost per translation: ~$0.04
- 100 articles × 10 languages = $40

**Tips to reduce costs**:
1. Reduce `TARGET_LANGUAGES` in `backend/apps/workers/tasks/translate.py`
2. Only translate high-priority articles
3. Set translation confidence threshold higher to avoid re-translations

## Troubleshooting

### Translations Not Working

**Check API Key**:
```bash
cd backend
python manage.py shell
```
```python
from django.conf import settings
print(settings.ANTHROPIC_API_KEY)  # Should print your key
```

**Check Celery Workers Running**:
```bash
ps aux | grep celery
# Should show 2 processes: worker and beat
```

**Check Redis Connection**:
```bash
redis-cli ping
# Should return: PONG
```

### Translation Stuck in DRAFT

Translations with confidence < 0.85 are saved as drafts for manual review:

1. Go to Django admin: http://localhost:8000/admin/
2. Navigate to **News** → **Translations**
3. Find the draft translation
4. Review content
5. Change status to **PUBLISHED** if quality is acceptable

### API Rate Limits

Anthropic has rate limits. If you hit limits, you'll see errors in Celery logs:

```
[ERROR] Translation failed abc123 → es: Rate limit exceeded
```

Solution: The task will auto-retry after 2 minutes (configured in `@shared_task` decorator).

## Disabling Translations

To disable translations (e.g., to save costs):

1. Remove or comment out `ANTHROPIC_API_KEY` in `.env`:
   ```bash
   # ANTHROPIC_API_KEY=
   ```

2. Restart Celery workers

3. Articles will still be fetched and processed, but translations will be gracefully skipped with a warning log.

## Advanced Configuration

### Customizing Target Languages

Edit `backend/apps/workers/tasks/translate.py`:

```python
# Only translate to English and Spanish
TARGET_LANGUAGES = ['en', 'es']
```

### Adjusting Confidence Threshold

Edit `backend/apps/workers/tasks/translate.py`:

```python
# Change line 80
status = 'PUBLISHED' if result.confidence >= 0.90 else 'DRAFT'  # More strict
```

### Translation Rate Limiting

Edit task decorator in `translate.py`:

```python
@shared_task(bind=True, max_retries=3, rate_limit='5/m')  # Slower rate
def translate_article(self, article_id: str, target_lang: str):
    # ...
```

## Support

For issues or questions:
- Check Celery worker logs for errors
- Verify API key is correct and has credits
- Ensure Redis is running: `redis-cli ping`
- Check Anthropic status page: https://status.anthropic.com/
