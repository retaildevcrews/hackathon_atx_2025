# Implementation Plan — Rubric–Criteria Composition Refactor

## Pre-flight

- [ ] Inventory existing rubrics and capture count + max criteria per rubric (log at INFO)
- [ ] Verify current `criteria_json` shape consistent (`criteria_id` + `weight` keys post-weight enhancement)
- [ ] Decide whether to keep `criteria_json` column temporarily (set `KEEP_CRITERIA_JSON=true` default)
- [ ] Add env flag placeholders: `DISABLE_JSON_CRITERIA_BACKFILL` (default false)
- [ ] Confirm no UI code depends on internal storage style (responses unchanged)

## Implementation

- [ ] Create ORM model `rubric_criterion_orm.py`
  - Fields: id (PK), rubric_id (FK->rubrics.id, cascade delete), criterion_id (FK->criteria.id, restrict), position (int), weight (float), created_at, updated_at
  - Unique constraint (rubric_id, criterion_id)
  - Index on (rubric_id, position)
- [ ] Update `rubric_orm.py` to add relationship `criteria_assoc = relationship("RubricCriterionORM", back_populates="rubric", order_by="RubricCriterionORM.position", cascade="all, delete-orphan")`
- [ ] Add reciprocal relationship in `RubricCriterionORM`
- [ ] Metadata create new table at startup (before seeding/backfill)
- [ ] Backfill routine (in `backfill_service.py`):
  1. Query all rubrics
  2. For each rubric with empty `criteria_assoc` and non-null/ non-empty `criteria_json`:
     - Parse JSON
     - De-duplicate while preserving first occurrence (warn if duplicates found)
     - Insert rows with enumerated position
     - Log success count
  3. Aggregate summary log (#rubrics migrated, #already modern, #skipped errors)
- [ ] Service layer (create rubric): replace JSON building with constructing assoc objects list
- [ ] Service layer (update draft rubric): delete existing assoc rows then insert new sequence
- [ ] Service layer (get/list): serialize from relationship (ignore `criteria_json` unless fallback needed)
- [ ] Remove writes to `criteria_json` (if KEEP_CRITERIA_JSON true: still leave last JSON for debuggability, else set to empty string)
- [ ] Publish logic unchanged (still blocks modification)
- [ ] Criterion delete (future-proof): implement guarded function raising 409 if referenced (optional placeholder)

## Validation

- [ ] Unit test: create rubric persists correct number of association rows with ordered positions
- [ ] Unit test: update rubric reorder sequence updates position values accurately
- [ ] Unit test: publish then update fails (409)
- [ ] Unit test: delete draft rubric cascades (rows removed)
- [ ] Unit test: duplicate criterion in create payload rejected (existing validation reused)
- [ ] Backfill test: simulate legacy rubric (manually insert JSON, no assoc rows) then run backfill; assert rows created
- [ ] Fallback test: if backfill disabled, ensure legacy rubric still served from JSON (temporary path)

## Samples and documentation

- [ ] Update README rubric section to note normalized storage (no external behavior change)
- [ ] Add migration note: automatic backfill at startup; disable via env if needed
- [ ] Add developer doc comment in `rubric_orm.py` marking `criteria_json` deprecated

## Rollout

- [ ] Introduce env flags in config module
- [ ] Deploy to dev; verify startup logs show backfill summary
- [ ] Run docker compose build/run smoke tests
- [ ] Remove/deprecate `criteria_json` in a later iteration (tracked separately)

## Manual Smoke Test Checklist

- Create rubric (POST) → verify DB join rows inserted
- Update rubric reorder (PUT) → positions reflect new order
- Publish then update → 409
- List rubrics → criteria order matches positions
- Delete draft rubric → join rows gone
- Backfill scenario: manually insert legacy JSON-based rubric, restart, confirm migration

## Risks & Mitigations

- Startup latency if many rubrics: can batch commit every N rubrics; acceptable hackathon scale
- Partial migration error: log and continue; rubric served from JSON until fixed
- Race conditions during backfill: perform before app ready to serve (run in startup event before router mount or first request)

## Follow-up (Post-Refactor)

- Drop `criteria_json` column
- Add analytic queries leveraging join table
- Add composite index for (criterion_id) filtering across rubrics
- Implement criterion deletion guard endpoint logic

## Completion Definition

- All new rubrics use join table only
- Existing rubrics migrated (unless backfill disabled intentionally)
- Tests for create/update/publish/delete/backfill pass
- README updated and passes lint
