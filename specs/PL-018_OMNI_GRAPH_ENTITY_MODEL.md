# Design Spec: PL-018 Omni-Graph Universal Entity Model

**Issue:** #018 / PL-018
**Status:** 📋 PLANNED (Phase 2)
**Last Updated:** 2026-02-21

## 1. Problem: The Fragmented Entity Schema

The current Phase 1 schema has one model per entity type:

```
Driver      → ArticleDriver   (through-table)
Team        → ArticleTeam
Circuit     → ArticleCircuit
Race        → ArticleRace
```

**Limitations:**
- To track a new entity type (e.g., `Staff`, `Mechanic`, `Engineer`, `WAG`) → need a new model + migration + through-table + update extractor
- `F1EntityExtractor` only handles Drivers and Teams — hardcoded to two model classes
- The Paddock Social Registry (PL-010) needs 2000+ staff records, which don't fit the Driver/Team schema
- Adding sponsors, manufacturers, or team principals as article entities requires more schema changes

## 2. Solution: JSONB-Powered Universal Entity Model

Replace the fragmented per-type models with a single `Entity` model.
Flexible attributes stored in `metadata` (JSONB) instead of fixed columns.

### 2.1 `Entity` Model

```python
class EntityType(models.TextChoices):
    DRIVER      = 'DRIVER',      'Driver'
    TEAM        = 'TEAM',        'Team'
    CIRCUIT     = 'CIRCUIT',     'Circuit'
    RACE        = 'RACE',        'Race'
    STAFF       = 'STAFF',       'Staff / Engineer / Mechanic'
    BRAND       = 'BRAND',       'Brand / Sponsor / Manufacturer'
    PERSON      = 'PERSON',      'Generic Person (WAG, Pundit, etc.)'

class Entity(models.Model):
    id          = CharField(32, primary_key)
    entity_type = CharField(choices=EntityType)
    name        = CharField(200, db_index)       # canonical display name
    slug        = SlugField(200, unique)
    code        = CharField(10, null, db_index)  # e.g., "VER", "FER"

    # Flexible attributes per entity type
    metadata    = JSONField(default=dict)
    # Examples:
    #   DRIVER: {"nationality": "Dutch", "number": 1, "team_code": "RBR"}
    #   STAFF:  {"role": "Chief Technical Officer", "team_code": "MER"}
    #   BRAND:  {"category": "TITLE_SPONSOR", "website": "..."}

    # Link back to the concrete model (Phase 1 compatibility)
    driver      = ForeignKey('teams.Driver', null, blank)
    team        = ForeignKey('teams.Team', null, blank)
    circuit     = ForeignKey('circuits.Circuit', null, blank)

    is_active   = BooleanField(default=True)
    created_at  = DateTimeField(auto_now_add)
    updated_at  = DateTimeField(auto_now)

    class Meta:
        db_table = 'entities'
        indexes = [
            Index(fields=['entity_type', 'slug']),
            Index(fields=['entity_type', 'is_active']),
        ]
```

### 2.2 Universal `ArticleEntity` Through-Table

Replaces all separate through-tables (`ArticleDriver`, `ArticleTeam`, etc.):

```python
class ArticleEntity(models.Model):
    article    = ForeignKey(Article, on_delete=CASCADE, related_name='article_entities')
    entity     = ForeignKey(Entity, on_delete=CASCADE, related_name='article_mentions')
    is_primary = BooleanField(default=False)
    score      = FloatField(default=0.0)  # relevance score from extractor

    class Meta:
        db_table = 'article_entities'
        unique_together = [['article', 'entity']]
```

## 3. Migration Strategy (Non-Breaking)

This is a **phased migration** — the Phase 1 models (`Driver`, `Team`, etc.) remain intact.

### Phase A: Add `Entity` table alongside existing models
- Create `Entity` model and `ArticleEntity` through-table
- Write a migration command: `python manage.py seed_entities` that populates `Entity` rows from existing `Driver`, `Team`, `Circuit` records, with `driver`/`team`/`circuit` FK back-references

### Phase B: Update `F1EntityExtractor` to query `Entity`
- Replace `Driver.objects.all()` + `Team.objects.all()` with `Entity.objects.filter(is_active=True)`
- Single query, supports all entity types including Staff
- Back-populates `ArticleEntity` instead of `ArticleDriver` / `ArticleTeam`

### Phase C: Update API serializers
- Expose `article_entities` (with `entity_type`, `name`, `is_primary`) instead of separate `drivers` / `teams` lists
- Keep legacy `drivers` / `teams` fields in response during transition period

### Phase D (Future): Deprecate separate through-tables
- Once all consumers use `article_entities`, remove `ArticleDriver`, `ArticleTeam`, etc.

## 4. Relationship to PL-010 (Paddock Social Registry)

The `SocialHandle` model proposed in PL-010 links to `entity_id`.
With the universal `Entity` model, `SocialHandle.entity` can point to any entity type
(Driver, Staff, Team) without per-type FK columns.

```
SocialHandle.entity → Entity(type=STAFF, name="James Allison", metadata={"role": "CTO"})
SocialHandle.entity → Entity(type=DRIVER, name="Lewis Hamilton")
```

## 5. What This Unlocks

| Capability | Without #018 | With #018 |
| :--- | :--- | :--- |
| Track staff/engineers in articles | ❌ No model | ✅ `STAFF` EntityType |
| Add new entity types | ❌ New model + migration | ✅ New `EntityType` enum value |
| Social handle for any person | ❌ Only Driver FK | ✅ Universal Entity FK |
| Historical RAG context (PL-015) | ❌ Fragmented | ✅ Single `Entity` graph |
| Entity extractor coverage | Drivers + Teams only | All registered types |

## 6. Success Criteria

- [ ] `Entity` model and `ArticleEntity` through-table created
- [ ] `seed_entities` command back-fills from existing Driver/Team/Circuit records
- [ ] `F1EntityExtractor` queries `Entity` table instead of per-type models
- [ ] API response includes `entities` array with `entity_type` field
- [ ] Phase 1 through-tables (`ArticleDriver`, `ArticleTeam`) remain intact during transition
