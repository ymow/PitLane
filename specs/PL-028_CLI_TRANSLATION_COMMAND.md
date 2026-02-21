# Design Spec: PL-028 CLI-Based Translation Management Command

**Issue:** RSS-001 (Translation Backfill)
**Status:** 📋 PLANNED
**Last Updated:** 2026-02-21

## 1. Problem

The existing translation pipeline (`translate_article` Celery task) requires `ANTHROPIC_API_KEY`.
When the key is absent, the task silently skips with `reason: 'api_key_missing'`.

This creates a cost barrier for batch translation during development or backfill operations —
especially when 100+ articles need zh-TW translations in one session.

## 2. Solution: Claude Code CLI as Translation Engine

Use the `claude` CLI (Claude Code) as a zero-API-cost translation engine via subprocess.
The management command pipes article content to `claude -p "<prompt>"` and saves the result
directly to the `Translation` model — bypassing Celery and the Anthropic SDK entirely.

```
Article (DB) → management command → claude CLI subprocess → parse JSON → Translation (DB)
```

This is the same AI quality as the API, but billed through the Claude Code subscription
rather than API tokens.

## 3. Command Interface

```bash
# Translate all untranslated articles to zh-TW (default)
python manage.py translate_cli

# Specify target language
python manage.py translate_cli --lang zh-TW

# Limit batch size
python manage.py translate_cli --lang zh-TW --limit 50

# Translate a specific article by ID or slug
python manage.py translate_cli --article <id_or_slug>

# Dry run (show what would be translated, don't save)
python manage.py translate_cli --dry-run
```

## 4. Implementation

**Location:** `backend/apps/translator/management/commands/translate_cli.py`

### 4.1 Core Logic

```python
import subprocess, json
from apps.news.models import Article, Translation
from apps.translator.claude_service import ClaudeTranslator  # reuse PRESERVE_TERMS + prompt builder

def translate_via_cli(title, body, source_lang, target_lang) -> dict:
    prompt = build_prompt(title, body, source_lang, target_lang)  # reuse existing _build_prompt logic
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True, text=True, timeout=120
    )
    return json.loads(result.stdout)
```

### 4.2 Reuse Existing Prompt

Reuse `ClaudeTranslator._build_prompt()` and `PRESERVE_TERMS` from `translator/claude_service.py`
to ensure terminology consistency between CLI and API translation paths.

### 4.3 Article Selection Query

```python
# Find articles missing a translation for the target language
articles = Article.objects.exclude(
    translations__lang=target_lang
).filter(
    translations__status='PUBLISHED'  # only articles with at least one published translation
).order_by('-published_at')[:limit]
```

### 4.4 Save Result

Reuse the same save logic as `translate_article` Celery task:
- `status = 'PUBLISHED' if confidence >= 0.85 else 'DRAFT'`
- Invalidate cache keys: `article:{slug}:{lang}` and `latest:news:{lang}`

## 5. Error Handling

| Scenario | Behaviour |
| :--- | :--- |
| `claude` CLI not found | Print clear error: "Claude Code CLI not installed. Run: npm install -g @anthropic-ai/claude-code" |
| CLI timeout (>120s) | Skip article, log warning, continue to next |
| Invalid JSON response | Retry once with a stricter prompt, then skip |
| Article already translated | Skip silently |
| `--dry-run` flag | Print article titles only, no DB writes |

## 6. Success Criteria

- [ ] Command exists at `apps/translator/management/commands/translate_cli.py`
- [ ] `--lang`, `--limit`, `--article`, `--dry-run` flags all work
- [ ] Reuses `ClaudeTranslator` prompt and `PRESERVE_TERMS` (no prompt duplication)
- [ ] Saves `Translation` records with correct `status` and `confidence`
- [ ] Graceful error handling when `claude` CLI is unavailable

## 7. Relationship to Existing Pipeline

| | Celery `translate_article` | `translate_cli` command |
| :--- | :--- | :--- |
| **Trigger** | Automatic (post-fetch) | Manual / scheduled cron |
| **Auth** | `ANTHROPIC_API_KEY` | Claude Code CLI session |
| **Use case** | Production real-time | Dev backfill / cost saving |
| **Prompt** | `ClaudeTranslator` | Same (reused) |
| **Output** | `Translation` model | `Translation` model (same) |
