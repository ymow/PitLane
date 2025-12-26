# Strategic Plan: Processor & Pipeline Optimization

## 1. Understanding the Goal
The objective is to address three critical "Day 2" stability issues in the PitLane aggregation pipeline to ensure high data quality and system reliability:
1.  **Ambiguity:** Fixing inaccurate Entity Extraction (e.g., confusing personal names with team names).
2.  **Duplication:** Replacing brittle title matching with robust content fingerprinting (SimHash) to catch syndicated content.
3.  **Race Conditions:** Preventing multiple workers from processing the same article simultaneously using distributed locks.
4.  **Language Fragmentation:** Ensuring foreign language content is correctly categorized and tagged via localized normalization.

## 2. Investigation & Analysis

### Current State Analysis
*   **Deduplication (`backend/apps/processor/deduplicator.py`):**
    *   Currently uses `difflib.SequenceMatcher` (fuzzy string matching) on **Titles only**.
    *   **Weakness:** Misses syndication where titles change slightly but the body is identical. It is also computationally expensive (O(N*M)) as the database grows.
*   **Entity Extraction (`backend/apps/processor/entity_extractor.py`):**
    *   Uses simple string matching against a dictionary of loaded Drivers/Teams.
    *   **Weakness:** No context awareness or negative lookaheads (e.g., matches "Williams" in any context).
*   **Concurrency:**
    *   Celery tasks (`fetch_single_source`) run in parallel without a locking mechanism, leading to potential duplicate database entries for the same URL.

## 3. Proposed Strategic Approach

### Phase 1: Robust Deduplication (SimHash)
*Goal: Eliminate syndicated spam and "Updates" noise.*

1.  **Model Migration:** Add a `simhash` field (BigInteger) to the `Article` model.
2.  **Upgrade `Deduplicator` Service:**
    *   **Mechanism:** Tokenize the article body and compute a 64-bit SimHash fingerprint.
    *   **Comparison:** Use Hamming Distance to identify similarity. If the bit distance between two hashes is < 3, they are considered duplicates.
    *   **Workflow:** Compute hash on fetch -> Query DB for similar hashes within a 24-hour window -> Flag as duplicate if match found.

### Phase 2: Context-Aware Entity Extraction
*Goal: Fix "The Bottas Problem" using lightweight NER.*

1.  **Introduce Spacy:** Integrate the `spacy` library with the `en_core_web_sm` model for local CPU-based Named Entity Recognition (NER).
2.  **Context Tuples:** Refactor the extractor to identify entities as `PERSON` or `ORG` before matching against the database.
3.  **Negative Constraints:** Implement filters to ignore common false positives (e.g., "Serena Williams", "Hamilton Watch").

### Phase 3: Concurrency Safety (Distributed Locks)
*Goal: Ensure idempotent processing.*

1.  **Redis Distributed Locks:** Use Redis (via `python-redis-lock` or custom implementation) to lock the processing of a specific URL.
2.  **Workflow:** 
    *   Worker acquires lock for `LOCK:PROC:<URL_HASH>`.
    *   If lock exists, the worker aborts (another worker is already handling it).
    *   If no lock, process and save to DB.

### Phase 4: Language Normalization
1.  **Localized Regex:** Expand `ArticleCategorizer` to support language-specific patterns (e.g., "Qualifiche" for Italian, "Clasificación" for Spanish).
2.  **Metadata Extraction:** For non-English feeds, use a lightweight translation of the Title/First Paragraph to English specifically for entity extraction, while preserving the original body for the user.

## 4. Verification Strategy

### Automated Tests
*   **SimHash Validation:** Test with articles that have identical bodies but different titles (syndication).
*   **Entity Precision:** Test with sentences like "Williams won the race" (Match Team) vs "Serena Williams played tennis" (No Match).
*   **Lock Test:** Simulate concurrent Celery workers picking up the same RSS item and verify only one `Article` record is created.

## 5. Implementation Status ✅

### ✅ **COMPLETED** - Phase 1: Robust Deduplication (SimHash)
- **SimHash Field**: Added to Article model (`backend/apps/news/models.py:111`)
- **Deduplicator Service**: Implemented with 64-bit SimHash fingerprinting (`backend/apps/processor/deduplicator.py`)
- **Backfill Command**: Created management command for existing articles (`backend/apps/news/management/commands/backfill_simhash.py`)
- **Testing**: Comprehensive test suite covering syndicated content detection (`backend/apps/processor/tests.py`)

### ✅ **COMPLETED** - Phase 2: Context-Aware Entity Extraction  
- **Spacy Integration**: NER model loaded in worker processes (`backend/apps/workers/tasks/process.py:18-28`)
- **Entity Extractor**: Context-aware matching with database entities (`backend/apps/processor/entity_extractor.py`)
- **Testing**: Tests for false positive prevention and context scoring (`backend/apps/processor/tests.py`)

### ✅ **COMPLETED** - Phase 3: Concurrency Safety (Distributed Locks)
- **Redis Locks**: Implemented in `fetch_single_source` task (`backend/apps/workers/tasks/fetch.py:32-44`)
- **Graceful Degradation**: Falls back to synchronous processing when Redis unavailable
- **Testing**: Mock tests for lock acquisition and failure scenarios (`backend/apps/processor/tests.py`)

### ✅ **COMPLETED** - Phase 4: Language Normalization
- **Localized Patterns**: Extended categorizer with 7 languages (EN, IT, ES, FR, DE, PT, NL) (`backend/apps/processor/categorizer.py:13-68`)
- **Categories Covered**: Breaking news, race reports, qualifying, technical, transfers, penalties
- **Fallback Logic**: Language-specific patterns with English fallback

### ✅ **NEW** - Performance Monitoring & Diagnostics
- **Memory Monitoring**: Spacy model loading and processing memory tracking (`backend/apps/processor/monitoring.py`)
- **Performance Decorators**: Function-level memory and execution time monitoring
- **Management Commands**: Memory status diagnostics (`backend/apps/processor/management/commands/memory_status.py`)
- **Alerting**: Automatic warnings for high memory usage (>500MB RSS)

## 6. Anticipated Challenges & Considerations

### ✅ **RESOLVED**
*   **Backfilling**: ✅ Management command created with batch processing and dry-run support
*   **Spacy Overhead**: ✅ Memory monitoring implemented with alerts and caching metrics
*   **Hamming Distance Performance**: ✅ Time-window filtering (24h) implemented to limit search scope

### 🔄 **ONGOING MONITORING**
*   **Production Performance**: Monitor memory usage during peak race weekends using `python manage.py memory_status --detailed`
*   **Deduplication Accuracy**: Review duplicate detection rates and adjust thresholds if needed
*   **Entity Extraction Precision**: Monitor false positives and update context patterns

## 7. Usage & Deployment

### Running Backfill (One-time)
```bash
# Dry run first
python manage.py backfill_simhash --dry-run

# Execute with batch size
python manage.py backfill_simhash --batch-size=50
```

### Memory Monitoring
```bash
# Quick status
python manage.py memory_status

# Detailed diagnostics  
python manage.py memory_status --detailed
```

### Running Tests
```bash
# All processor tests
python manage.py test apps.processor.tests

# Specific test cases
python manage.py test apps.processor.tests.SimHashDeduplicationTests
```

### Performance Metrics
- Memory monitoring automatically caches metrics to Redis (5min TTL)
- Spacy model loading typically uses 150-200MB RAM
- Alert threshold set at 500MB RSS memory usage
- Execution time logging for all processor operations
