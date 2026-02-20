# PitLane: Universal Domain Intelligence Engine - Master Spec

## 1. Vision & Core Principles
PitLane is an agentic CMS platform using real-time data and entity graphs to deconstruct complex industries.
- **North Star**: Empower fans with "Team Principal" level intelligence through LLM-driven causal inference and real-time telemetry.
- **Spec-Driven**: All development follows the Superpowers methodology (Design -> Plan -> TDD -> Execute).
- **Domain Agnostic**: The engine supports pluggable templates (F1, Movies, etc.).

## 2. Current Phase: Phase 1 - 2026 Season Readiness
We are currently focusing on the foundation for the 2026 F1 season.

### 2.1 Paddock Social Registry (Active)
Establishing a comprehensive database of 2000+ paddock personnel handles (Mechanics, Engineers, WAGs) without active content analysis yet.
- **Issue**: [DON-12 / PL-010]

### 2.2 Open Live Data Integration (Active)
Ensuring stable telemetry flow using open-source data streams (OpenF1).
- **Issue**: [DON-5 / PL-006]

### 2.3 2026 Schema Sync (Planned)
Updating the grid to reflect the 2026 Audi/Sauber transition and driver transfers.
- **Issue**: [DON-7 / PL-003]

### 2.4 News & Intelligence (Active)
Real-time news aggregation from multiple sources with automated translation and entity extraction.
- **RSS Pipeline**: Multi-source fetching with deduplication (SimHash).
- **Translation**: Automated zh-TW translation fallback via CLI/LLM.
- **Entity Extraction**: Hybrid approach using Regex fallback (in absence of spaCy) for robust F1 entity recognition.
- **Frontend**: Dynamic article loading with fallback to zh-TW content.

## 3. Deferred Visions (Backlog)
The following are high-value features postponed to Phase 2/3:
- **F1 TV Pro SignalR Client**: High-fidelity official stream (Requires paid account).
- **Social Media Intelligence**: VLM-based OCR and relationship discovery from screenshots/stories.
- **Historical RAG**: Vectorizing 70+ years of F1 history.

## 4. Technical Architecture
- **Backend**: Django 5.x + Celery + Redis + Postgres.
- **Frontend**: React 19 + Vike + Tailwind 4 + Base UI.
- **Entity Model**: Moving towards a JSONB-powered EAV (Issue #018).
