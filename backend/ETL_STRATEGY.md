# ETL Strategy: Toward Entity-Relationship Extraction

## 1. Extract
- Ingest from RSS, Web Scrapers, and Social Media APIs.
- Assign a unique `external_id` based on MD5(URL).

## 2. Transform (The Agentic Brain)
- **Deduplication**: SimHash body matching.
- **Mapping**: Link data to the Omni-Graph (`Entity` model).
- **Normalization**: Standardize driver names and team identities across languages.

## 3. Load
- Multi-step persistence: Article -> Chunks -> Entities -> Relationships.
