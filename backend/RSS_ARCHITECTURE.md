# RSS & Social Ingestion Architecture

## 1. Overview
The ingestion layer serves as the "ears and eyes" of PitLane. It handles both structured RSS feeds and social media signals.

## 2. Ingestion Channels
- **RSS (Classical)**: 15+ premium sources.
- **Social Registry (New)**: 2000+ handles across IG/Twitter.
- **Official Data**: Jolpica/OpenF1 streams.

## 3. Workflow
1. **Fetch**: Celery Beat schedules task.
2. **Standardize**: Content mapped to universal Entity/Relation models.
3. **Notify**: Real-time signals pushed to Frontend Live Ticker.
