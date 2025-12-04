# PitLane Article Architecture Refactoring Strategy

## 1. Overview
This document outlines the strategy to refactor the `Article` architecture to support **Content Chunking**, **GEO (Generative Engine Optimization)**, and **SEO**. The goal is to move from a "blob-based" storage model to a structured, semantic model that powers AI features and search visibility.

## 2. Core Architecture Changes

### A. Data Modeling (Schema)

#### 1. `ArticleChunk` (New Model)
To support RAG (Retrieval-Augmented Generation) and precise content processing, we will split article bodies into chunks.

- **Relationships**: `ForeignKey` to `Article`.
- **Fields**:
    - `sequence` (int): Order of the chunk.
    - `content` (text): The actual text/HTML content.
    - `chunk_type` (enum): `HEADING`, `PARAGRAPH`, `LIST`, `QUOTE`.
    - `embedding` (vector, optional for now): For future vector search.

#### 2. Enhanced Relationships (Existing Through Models)
We will actively utilize the `is_primary` field in existing through models (`ArticleDriver`, `ArticleTeam`).

- **Logic**:
    - **Primary**: Entities mentioned in the **Title** or **First Paragraph**, or with high frequency.
    - **Secondary**: Entities mentioned incidentally.

### B. Processing Pipeline (`process_article`)

The current simple `.add()` logic will be replaced with a sophisticated 3-step process:

1.  **Smart Extraction**:
    - The `F1EntityExtractor` will return entities with a "score" or "position".
    - Logic: `IF entity IN title OR count > 3 THEN is_primary=True`.
2.  **Bulk Association**:
    - Use `ArticleDriver.objects.bulk_create(...)` to persist relationships with the correct `is_primary` flag.
3.  **Intelligent Chunking**:
    - Parse `original_body` (HTML).
    - Split by block-level tags (`<p>`, `h2`, `ul`).
    - Save as `ArticleChunk` records.

### C. API & Output

- **Serializers**: Updated to expose `is_primary` flags to the frontend.
- **SEO/GEO**: The frontend will use the `is_primary` Driver/Team/Category to generate:
    - **Canonical URLs**: `/news/{primary_category_slug}/{article_slug}`
    - **Schema.org JSON-LD**: Identifying the "main entity" of the page.

## 3. Implementation Steps

### Phase 1: Logic Upgrade (Backend)
1.  **Refactor `F1EntityExtractor`**: Return rich objects `(Entity, score)` instead of flat lists.
2.  **Update `process_article`**: Implement `bulk_create` for associations.

### Phase 2: Model Update
1.  Create `ArticleChunk` model.
2.  Implement HTML splitter utility.

### Phase 3: API Exposure
1.  Update `ArticleDetailSerializer` to include `chunks` and rich entity relationships.

## 4. Future Proofing
This architecture prepares PitLane for:
- **Vector Search**: Searching specific *paragraphs* rather than whole articles.
- **AI Summaries**: Generating summaries based on specific chunks.
- **Dynamic Context**: Providing AI chatbots with only relevant chunks of an article.
