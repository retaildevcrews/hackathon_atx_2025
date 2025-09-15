fea# Rubric Support (Criteria API)

## Problem

Current API manages individual criteria but lacks a higher-level grouping to bundle sets of criteria for consistent evaluation scenarios (e.g., "Security Baseline" or "Innovation Review"). Teams must manually select criteria each time, creating repetition and inconsistency. We need a reusable, versionable grouping construct.

## Goals (acceptance criteria)

- Can create a rubric with unique name, description, and an ordered list of criteria IDs.
- Duplicate rubric names rejected (case-insensitive).
- Rubric can be updated until published; publish locks modifications.
- Retrieve rubric by id or by name (latest published or draft).
- Validate all referenced criteria exist; duplicates in list rejected.
- Optional per-criterion weight persisted (0–1 inclusive).
- Listing endpoint supports filtering by name substring.
- OpenAPI docs auto-reflect new models.

## Non-goals

- Score aggregation logic.
- Permissions / ownership model.
- Rubric cloning or branching version trees.
- Advanced search (full text across criteria definitions).
- Soft delete (hard delete only for drafts this iteration).

## Design

- Add new ORM model `RubricORM` storing metadata + JSON array of rubric entries.
- Use `criteria_json` TEXT column to hold array of `{criteriaId, weight?}` for simplicity (migrating to a join table later if needed).
- Enforce uniqueness via normalized lowercase name column or application-level check (app-level w/ index later).
- Version initially fixed at `1.0.0`; publish flips `published` flag and sets `published_at`. Future updates would create a new record (out of scope now).
- Service layer handles creation, mutation guard (409 if published), and criteria existence check: single IN query over provided IDs.
- Pydantic schema parallels ORM, exposing `criteria` list and publication metadata.
- Add `expand=criteria` query param to include basic details (id, name, description) fetched in one query (optional if time).

## Impacted code

- `apps/criteria_api/app/models/rubric_orm.py` (new)
- `apps/criteria_api/app/models/rubric.py` (Pydantic schemas)
- `apps/criteria_api/app/services/rubric_service.py` (CRUD + publish)
- `apps/criteria_api/app/routes/rubrics.py` (API endpoints)
- `apps/criteria_api/app/main.py` (include router)
- Potential shared util: `app/utils/validation.py` (criteria existence, name pattern)

## Edge cases and risks

- Creating rubric with 0 criteria (decide: allow? For now: allow but warn later) – risk of meaningless rubric.
- Very large rubric ( >200 criteria ) causing slow validation – mitigate with length cap.
- Concurrent publish & update race – last writer wins without optimistic locking; acceptable for hack.
- Criteria deleted after rubric creation (stale references) – not handled yet.

## Test plan

- Create rubric: success (201) + retrieval (GET).
- Duplicate name: 409.
- Publish then attempt update: 409.
- Invalid criteria id: 400.
- Delete draft: 204.
- Expand parameter returns criteria detail objects.

## Migration/compat

- Add table via SQLAlchemy metadata create (no Alembic yet). Existing functionality unaffected.
- Future migration path: add unique index & join table if scaling.

## Rollout

- No feature flag (simple immediate availability).
- Basic logging via existing FastAPI logging (INFO create/update/publish).
- Add minimal README section in API docs for Rubrics.

## Links

- N/A (new feature).
