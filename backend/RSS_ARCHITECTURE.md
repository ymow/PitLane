# PitLane RSS Feed Mechanism Architecture

## Overview
The RSS mechanism in PitLane is designed as an **event-driven, asynchronous pipeline**. It is responsible for ingesting news from various F1 sources, normalizing the data, and triggering downstream processing (entity extraction and translation).

## Architecture Flow

1.  **Scheduler / Trigger**: A Celery beat schedule (or manual trigger) initiates the fetching process.
2.  **Fetcher (Worker)**: The `fetch_single_source` task pulls the RSS feed.
3.  **Normalization**: `RSSFetcher` parses XML into standardized `RSSItem` objects.
4.  **Deduplication**: The system checks for existing `external_id` (MD5 hash of GUID) to prevent duplicate articles.
5.  **Storage**: New articles are saved to the database as `Article` records.
6.  **Event Trigger**: Upon successful creation, the `process_article` task is immediately dispatched.

## Core Components

### 1. The Fetcher (`backend/apps/fetcher/rss.py`)
The `RSSFetcher` class is the core utility for parsing feeds.
- **Library**: Uses `feedparser` to handle RSS and Atom feeds.
- **Normalization**: Converts diverse feed formats into a unified `RSSItem` dataclass.
- **ID Generation**: Generates a deterministic `external_id` using MD5 hashing of the article's GUID or URL. This is critical for idempotency.

### 2. Celery Tasks (`backend/apps/workers/tasks/fetch.py`)
- **`fetch_sources_by_priority`**: Iterates through a list of source slugs and dispatches individual fetch tasks.
- **`fetch_single_source`**:
    - Fetches the feed for a specific source.
    - Checks `Article.objects.filter(external_id=...)` to skip existing items.
    - Creates `Article` objects.
    - **Crucially**: Chains the workflow by calling `process_article.delay(article.id)`.

### 3. Data Models (`backend/apps/news/models.py`)
- **`Source`**: Stores configuration (URL, Language, Priority, Fetch Interval).
- **`Article`**: Stores the raw fetched content (`original_title`, `original_body`) before any processing.

## Configuration
Sources are defined in `backend/apps/fetcher/sources.py` and seeded into the database. This allows for version-controlled management of feed sources while keeping the runtime dynamic.

## Error Handling
- **Retries**: Celery tasks are configured with `max_retries=3` to handle transient network failures.
- **Logging**: Comprehensive logging tracks fetch counts, parsing errors, and skipped duplicates.
