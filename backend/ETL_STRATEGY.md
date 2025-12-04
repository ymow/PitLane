# ETL Pipeline Implementation Plan

## 1. Overview
We are implementing a robust ETL (Extract, Transform, Load) pipeline to clean, deduplicate, and qualify news content before it reaches the frontend or translation layer.

## 2. Architecture

### A. Extraction (Fetcher)
- **Deduplication**: Implement `TitleSimilarity` check using `difflib` or Levenshtein distance to detect duplicate stories across sources.
- **Quality Check**: Basic validation (min length, image presence).

### B. Transformation (Processor)
- **Sanitization**: Use `bleach` to strictly scrub HTML content (remove scripts, styles, iframes).
- **Topic Extraction**: Add keyword-based topic tagging (e.g., "Interviews", "Technical", "Rumors").
- **Quality Scoring**: Calculate a `quality_score` (0-100).

### C. Load / Orchestration
- **Translation Policy**: Only queue translations if `quality_score > 50` OR `priority == HIGH/CRITICAL`.

## 3. Implementation Steps

### Step 1: Dependencies
- Add `bleach` and `python-Levenshtein` (optional, or use difflib) to `requirements.txt`.

### Step 2: Logic Implementation
- Create `backend/apps/processor/deduplicator.py` for similarity checks.
- Create `backend/apps/processor/sanitizer.py` for HTML cleaning.
- Update `backend/apps/workers/tasks/fetch.py` to use deduplicator.
- Update `backend/apps/workers/tasks/process.py` to use sanitizer and implement translation policy.

### Step 3: Database Update
- Add `quality_score` (float) and `is_duplicate` (bool) fields to `Article` model.
