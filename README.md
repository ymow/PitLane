# PitLane: Omni-Graph Intelligence Engine 🏎️

PitLane is a world-class, agentic Formula 1 intelligence platform. Beyond simple news aggregation, it is a **Domain Digital Twin** that synchronizes real-time telemetry, paddock social signals, and 70+ years of historical context into a single, LLM-driven "War Room" experience.

## 🌟 Vision: The "Team Principal" View
Our goal is to provide fans with the same level of intelligence available on a team's pit wall. We don't just report news; we deconstruct the causal relationships between technical regulations, financial constraints, and track performance.

## 🚀 Key Features (Phase 1: 2026 Readiness)
- **Omni-Graph Core**: A universal entity-relationship schema capable of tracking not just drivers, but every mechanic, engineer, and WAG in the paddock.
- **Open Live Telemetry**: Real-time sync with `api.openf1.org` for Speed, RPM, Gear, and Throttle data.
- **Agentic CMS**: A template-driven backend that can switch between F1, MotoGP, or Movies via YAML configuration.
- **AI-Powered Multi-language**: F1-specialized translations across 10+ languages using Claude AI.
- **Spec-Driven Development**: Powered by [Superpowers](https://github.com/obra/superpowers) and Linear.app integration.

## 🛠️ Technology Stack
- **Frontend**: React 19, Vike (SSR), Tailwind CSS v4, Base UI.
- **Backend**: Django 5.x, Django REST Framework, Celery, Redis, PostgreSQL.
- **AI/ML**: Anthropic Claude API (Translation & Inference), Spacy (NER), SimHash (Deduplication).
- **Data**: Jolpica (Historical/Results), OpenF1 (Live), FastF1 (Deep Analysis).

## 🏁 Quick Start (Developer Mode)
1. **Initialize Environment**: `pip install -r backend/requirements.txt`
2. **Database Setup**: `cd backend && python manage.py migrate`
3. **Linear Integration**: `python manage.py linear_auth` to connect your issue tracker.
4. **Run Dev Server**: `cd frontend && npm run dev`

---
*Built for the 2026 F1 season and beyond.*
