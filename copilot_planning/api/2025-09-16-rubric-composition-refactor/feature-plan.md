# Rubric–Criteria Composition Refactor

## Problem

Current implementation stores a rubric's criteria (and optional weights) as a JSON array inside a single `criteria_json` TEXT column on `RubricORM`. This opaque embedding limits:

- Strong relational integrity (no FK per association)
- Efficient querying (e.g., find all rubrics using a criterion)
- Incremental updates (must rewrite entire JSON blob)
- Potential future features (analytics, weight normalization, per-criterion scoring history)

A proper compositional relationship (rubric has many rubric_criteria rows; each rubric_criteria references a criterion + metadata like weight, position) enables scalability and clarity.

## Goals (acceptance criteria)

- Introduce normalized join table `rubric_criteria` with columns: id (PK), rubric_id (FK), criterion_id (FK), position (int), weight (float, non-null), created_at, updated_at.
- Rubric retrieval endpoints return ordered array of criteria with weight identical (no response shape regression) but now populated via join.
- Create/update rubric operations persist associations in join table inside a transaction.
- Deleting a draft rubric cascades to its rubric_criteria rows.
- Publishing rubric still locks modifications (associations immutable after publish).
- Criteria deletion (if implemented later) is prevented when referenced (FK constraint) or returns clear 409.
- Backfill / migration script migrates existing JSON-based rubrics into join table without data loss.

## Non-goals

- Version branching or historical lineage beyond current published flag.
- Soft delete for rubric or rubric_criteria.
- Advanced search or analytics endpoints (follow-up after normalization).
- UI changes (should remain unaffected functionally).

## Design

- New ORM model `RubricCriterionORM` with SQLAlchemy mapping.
- Remove reliance on `criteria_json` for new writes; optionally keep column during transition (deprecated) or drop once migration complete.
- Service layer changes:
  - On create: insert Rubric row, then bulk insert RubricCriterion rows with enumerated position.
  - On update (draft only): replace associations (delete existing rows, insert new set) or perform diff-based upsert (simpler: replace set).
  - On read: query Rubric + joined ordered associations sorted by `position`.
  - On publish: unchanged semantics.
- Migration strategy (since no Alembic currently):
  - At startup, detect if `rubric_criteria` table exists; if not, create via metadata.
  - If legacy rubrics have non-null `criteria_json`, parse and populate `rubric_criteria` if empty for that rubric (idempotent backfill).
  - Mark `criteria_json` usage deprecated in logs; leave column for fallback for now.
- Response model unaffected (still returns `criteria: [{criteria_id, weight}]`).
- Optional config flag `DISABLE_JSON_CRITERIA_BACKFILL` to skip auto-migration (default false).

## Impacted code

- `app/models/rubric_orm.py` (add relationship + possibly mark criteria_json deprecated comment)
- `app/models/rubric_criterion_orm.py` (new file)
- `app/models/rubric.py` (no structural change; ensure serialization pulls from relationship)
- `app/services/rubric_service.py` (create/update/get/list logic refactor; backfill logic)
- `app/seed/seed_data.py` (seed via new join table)
- `app/routes/rubrics.py` (unchanged interface; remove any JSON field assumptions)
- `app/main.py` (startup backfill invocation)
- Potential new: `app/services/backfill_service.py` for migration clarity

## Edge cases and risks

- Partial backfill failure (one rubric migrates, another fails) → risk of mixed storage; mitigation: transactional per-rubric with error log + skip repeated attempts after success flag.
- Duplicate criteria in legacy JSON (should not exist) — if encountered, collapse to first occurrence and warn.
- Concurrency during migration (requests arriving while backfilling) — mitigate by performing backfill before app starts accepting traffic.
- Performance: large rubrics (hundreds of criteria) bulk insert; use SQLAlchemy bulk operations.

## Test plan

- Create rubric → join rows created with correct weight + position.
- Update rubric reorder criteria → positions updated accordingly.
- Publish then attempt update → 409 unchanged.
- Backfill test: insert legacy JSON rubric manually, run startup, verify join rows populated and subsequent GET uses join.
- Delete draft rubric → join rows removed.
- Attempt to delete criterion referenced by rubric (future operation) → FK constraint blocks (simulate and expect IntegrityError mapped to 409).

## Migration/compat

- Transitional period where `criteria_json` retained but ignored for writes post-migration.
- Backfill ensures reads consistent; if backfill disabled, legacy rubrics still served by parsing JSON (temporary fallback) — documented limit.

## Rollout

- Add CHANGELOG entry: normalized rubric compositional model.
- Add environment flag to disable automatic backfill if operator wants manual control.
- Log metrics: number of rubrics migrated at startup.

## Links

- Weight enhancement plan: `copilot_planning/api/2025-09-16-rubric-weights/feature-plan.md`
