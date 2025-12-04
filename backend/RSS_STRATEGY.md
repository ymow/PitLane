# RSS Integration & Data Handling Strategy

## 1. Source Configuration
We will expand the `SOURCES` configuration to include all identified global markets.

### Organization
Sources will be organized by **Language/Region** in `backend/apps/fetcher/sources.py`.

### Schema
Each source entry requires:
```python
"slug": {
    "name": "Display Name",
    "feed_url": "https://...",
    "lang": "ISO Code (e.g., zh-TW)",
    "priority": int (80-100),
    "fetch_interval": int (seconds),
}
```

## 2. Fetching Best Practices

### "Polite" Fetching
- **User-Agent**: Update `RSSFetcher` to use `PitLaneBot/1.0` to identify our traffic.
- **Timeouts**: Enforce strict 10s timeouts to prevent worker hang.

### Data Sanitization
- **Encoding**: Explicitly handle UTF-8 for Asian languages.
- **Cleaning**: Strip "Read more" links and tracking pixels from RSS bodies before saving.

## 3. Implementation Plan (Backlog)

### Task 1: Source Expansion
- [ ] Update `backend/apps/fetcher/sources.py` with the full list of 30+ sources.
- [ ] Verify `feed_url` accessibility for all new sources.

### Task 2: Fetcher Hardening
- [ ] Modify `RSSFetcher` class to set custom User-Agent.
- [ ] Add `clean_body()` method to remove common RSS clutter.

### Task 3: Management Command
- [ ] Create `python manage.py sync_sources` to idempotently update the database from `sources.py`.

### Task 4: Validation
- [ ] Run `sync_sources`.
- [ ] Verify ingestion of non-English content (Chinese, Spanish).
