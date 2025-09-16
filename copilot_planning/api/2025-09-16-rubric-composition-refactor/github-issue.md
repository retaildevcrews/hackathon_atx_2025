# GitHub Issue: Refactor Rubric Storage to Compositional Model

## Title

Refactor rubric criteria storage to normalized join table (rubric_criteria)

## Summary

Migrate from JSON-embedded criteria inside `rubrics.criteria_json` to a normalized `rubric_criteria` join table enabling relational integrity, efficient queries, and future analytics.

## Motivation

Current opaque JSON storage blocks FK enforcement, complicates partial updates, and hinders querying (e.g., enumerate all rubrics using a given criterion). A compositional model reduces technical debt and prepares for weight-based scoring, analytics, and safe deletions.

## Acceptance criteria

- New table `rubric_criteria` persists rubric–criterion associations with position + weight.
- Create/update operations populate join table (no new writes to `criteria_json`).
- GET endpoints return identical response shape using join data.
- Deleting a draft rubric cascades deletion of associated rows.
- Publish still prevents modification of associations.
- Startup backfill migrates legacy rubrics unless disabled by env flag.

## Scope

Included:

- ORM model, service refactor, backfill routine
- Config flag `DISABLE_JSON_CRITERIA_BACKFILL`
- README update + developer deprecation note

Excluded:

- Dropping `criteria_json` column (follow-up)
- UI changes
- Analytics endpoints

## Out of scope

- Version history or branching
- Soft deletes
- Criterion deletion logic (guard only placeholder)

## Design overview

- Add `RubricCriterionORM` with FK to `RubricORM` and `CriterionORM`.
- Backfill: parse existing JSON arrays; create ordered association rows; idempotent.
- Service layer: replace JSON manipulation with relationship operations inside transaction.
- Response serialization unchanged (criteria list built from association rows).

## Impacted code

- `app/models/rubric_orm.py`
- `app/models/rubric_criterion_orm.py` (new)
- `app/services/rubric_service.py`
- `app/seed/seed_data.py`
- `app/main.py` (startup backfill)
- `README.md`

## Test plan

- Unit tests for create, update reorder, publish immutability, delete cascade
- Backfill test: legacy JSON → join rows
- Fallback (backfill disabled) served from JSON (temporary)

## Risks and mitigations

- Migration failure → per-rubric transactional backfill, logging summary
- Performance during startup → small scale acceptable; optimize later if needed
- Inconsistent state if mixed storage → always prefer join data when present

## Definition of Done

- All existing + new rubrics return from join table
- Legacy data migrated (unless explicitly disabled)
- Tests green; docs updated; lint passes
