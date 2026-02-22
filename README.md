# PitLane: Omni-Graph Intelligence Engine

PitLane is a **Universal Domain Intelligence Engine** — an LLM-driven, graph-based CMS that reconstructs complex industries in real time. Formula 1 is the first pilot scenario. The same architecture can be switched to MotoGP, cinema, or finance by swapping a YAML config file.

> "From F1 Paddock to Hollywood Red Carpet: One Engine, Infinite Intelligence."

---

## Why PitLane is Different

Traditional news platforms report *what* happened. PitLane answers *why* — by fusing real-time telemetry, paddock social signals, and 70+ years of historical context into a single LLM-driven War Room.

| Capability | Traditional CMS | PitLane |
|---|---|---|
| News aggregation | ✅ | ✅ |
| Multi-language | ❌ | ✅ 10+ languages |
| Live race telemetry | ❌ | ✅ Sub-second sync |
| Causal inference ("why Honda left") | ❌ | ✅ RAG + LLM |
| Paddock social monitoring (IG Stories) | ❌ | ✅ 2000+ accounts |
| Entity relationship graph | ❌ | ✅ Driver → WAG → Legend |
| Cross-domain template | ❌ | ✅ F1 → Movies → Finance |

---

## Four Core Pillars

**🏎️ Real-time Race Sync** — When lights go out, every car's telemetry is mirrored in the database. WebSocket push to frontend. Anomaly detection triggers automatic incident reports.

**🌍 Global Intelligence** — Claude AI translates with F1-specific terminology across 10+ languages. 2000+ paddock accounts monitored across X, Instagram, and TikTok.

**🧠 LLM Contextual Engine** — Historical RAG over regulations, Wikipedia, and F1 books. Causal inference links breaking news to decades of context. Auto-generates weekly deep-dive articles.

**🛠️ Universal CMS Template** — Domain-agnostic `Entity` + `Relationship` graph. Pluggable skill system. Switch domains by loading a new YAML config.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.x · Celery · Redis · PostgreSQL |
| Frontend | React 19 · Vike SSR · Tailwind CSS v4 · Base UI |
| AI | Anthropic Claude API (translation, inference) |
| NER | spaCy · SimHash |
| Live Data | OpenF1 (real-time) · Jolpica · FastF1 (analysis) |
| Vector DB | pgvector (Phase 3) |
| Dev Workflow | Spec-driven · Linear.app · Superpowers methodology |

---

## Roadmap

| Phase | Focus | Status |
|---|---|---|
| **Phase 1** | F1 2026 Pilot — news pipeline, live telemetry, social registry, 2026 grid | 🟡 In Progress |
| **Phase 2** | Graph & Abstraction — universal Entity model, paddock people graph, causal graph | ⚪ Planned |
| **Phase 3** | Intelligence — social ingestion, historical RAG, live race state machine | ⚪ Planned |
| **Phase 4** | Template & Expand — YAML domain config, skill interface, second domain pilot | ⚪ Planned |

See [SPEC.md](./SPEC.md) for the full issue backlog (22 issues) and technical architecture.

---

## Quick Start

```bash
# Backend
pip install -r backend/requirements.txt
cd backend && python manage.py migrate
python manage.py runserver

# Frontend
cd frontend && npm install && npm run dev
```

---

*Built for the 2026 F1 season. Designed for every domain beyond it.*
