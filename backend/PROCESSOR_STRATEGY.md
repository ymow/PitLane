# Processor Strategy: From Text to Intelligence

## 1. Pipeline Architecture
PitLane transforms raw RSS strings into structured graph nodes.

### Step 1: Sanitization & Chunking
- Use `bleach` for strict HTML cleaning.
- Break long articles into `ArticleChunk` for easier LLM processing and vector embedding.

### Step 2: Content Deduplication
- Use **64-bit SimHash** fingerprinting.
- Hamming distance < 3 identifies duplicated syndicated news.

### Step 3: Entity Extraction (NER)
- **Primary**: Spacy `en_core_web_sm` for Identifying Driver/Team nodes.
- **Goal**: Move toward universal `Entity` linking (Issue #018).

## 2. Intelligence Evolution (Omni-Graph)
Our processor is evolving from a news classifier to a relationship inferrer.
- **Social Registry**: Registering 2000+ handles to track staff movements.
- **Causal Linking**: Connecting events (e.g., Honda returning) to historical context (e.g., carbon neutral shift).

## 3. Implementation Challenges
- **Python 3.13 Compat**: Resolving `blis`/`thinc` compilation issues for Spacy on Darwin.
- **VLM Pipeline**: Planning for screenshot intelligence (recognizing technical parts from paddock photos).
