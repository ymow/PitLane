# F1 Data Strategy: Omni-Graph Hybrid Engine

## 1. Overview
PitLane synchronizes diverse data streams to create a digital twin of the F1 season. We prioritize reliability and low latency for Phase 1.

## 2. Data Sources

| Tier | Provider | Frequency | Data Points |
| :--- | :--- | :--- | :--- |
| **Historical** | **Jolpica (Ergast Mirror)** | Periodic | Standings, Results, Official Calendars. |
| **Open Live** | **OpenF1** | 2s Polling | Real-time Speed, RPM, Gear, Throttle. |
| **Deep Analysis** | **FastF1** | Post-Race | Lap-by-lap pace, Tyre degradation, Comparison charts. |
| **Intelligence** | **Paddock Registry** | Continuous | Technical staff movements, Social signals. |

## 3. Implementation Logic

### A. The RacingService
Located at `apps.api.services.RacingService`, this service centralizes:
- OpenF1 Session Key management.
- Post-race data enrichment for API views.

### B. Automation Pipeline
1. **Trigger**: Jolpica marks a race as `COMPLETED`.
2. **Task**: Celery invokes `fastf1_service.generate_charts`.
3. **Storage**: Charts saved to `media/telemetry_charts/` and linked to `RaceResult`.

## 4. Current Roadmap
- [x] Unify external API to Jolpica.
- [x] Implement sub-second telemetry widget.
- [ ] Seed 2026 Audi/Sauber transition data.
- [ ] (Future) Drive VTuber broadcast signals from OpenF1 events.
