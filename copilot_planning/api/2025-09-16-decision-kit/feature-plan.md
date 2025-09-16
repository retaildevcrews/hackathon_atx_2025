# Decision Kit Feature

## Problem

Rubrics and Candidates currently exist independently. Evaluators need a cohesive bundle that fixes a specific rubric version together with a chosen set of candidates to run comparative evaluation workflows (scoring, commentary, ranking) reliably. Without a "decision kit" construct, ad‑hoc pairing risks drift (rubric edits mid-process) and inconsistent candidate selection. A decision kit should snapshot the association between one rubric (draft or published) and selected candidates for a consistent evaluation session.

## Goals (acceptance criteria)

- Create a Decision Kit with: name (unique per org/system scope), description, rubric reference (by rubric id), and list of candidate ids.
- Rubric referenced must be published OR if draft then kit stores rubric version metadata (version number + published flag) preventing later mutation impact (still referencing immutable state if published, or capturing version for draft freeze — see non-goals for cloning rules).
- API returns kit detail including: id, name, description, rubric_id, rubric_version, rubric_published, candidates list (id, name snapshot), created_at, updated_at.
- Adding candidates validates existence; duplicates rejected.
- Cannot change rubric of an existing kit after creation (immutable association).
- Can add/remove candidates for a kit while kit is in "open" state (status = OPEN). (Optional lock status change endpoint; minimal initial status OPEN only.)
- List endpoint supports filtering by name substring.

## Non-goals

- Generating evaluation scores or decision report (future).
- Cloning or versioning decision kits.
- Cross-rubric kits (exactly one rubric per kit).
- Complex status lifecycle beyond OPEN (e.g., CLOSED, ARCHIVED) — deferred.
- Automatic copying/embedding of full rubric JSON into kit (store ids + version fields only this iteration).

## Design

### Data Model

- Table `decision_kits`:
  - id (PK)
  - name_original
  - name_normalized (unique)
  - description (text nullable)
  - rubric_id (FK -> rubrics.id)
  - rubric_version (int) (snapshot from rubric row)
  - rubric_published (bool) snapshot
  - status (text) default 'OPEN'
  - created_at, updated_at
- Table `decision_kit_candidates`:
  - id (PK)
  - decision_kit_id (FK -> decision_kits.id, cascade delete)
  - candidate_id (FK -> candidates.id, restrict delete)
  - position (int) (for ordering / ranking display) — initial sequential assignment
  - created_at
  - UNIQUE(decision_kit_id, candidate_id)

### API Endpoints (prefix `/decision-kits`)

- POST `/decision-kits` create kit (JSON: name, description?, rubric_id, candidate_ids[])
- GET `/decision-kits` list (+ optional `name_contains` query)
- GET `/decision-kits/{id}` detail (with candidates array ordered by position)
- PATCH `/decision-kits/{id}/candidates` replace or modify candidate list (body: candidate_ids[]). (Simple replace for MVP.)
- DELETE `/decision-kits/{id}` remove kit (allowed only while status OPEN)
- (Optional) POST `/decision-kits/{id}/lock` (future; not implemented now)

### Validation Rules

- Name required, <=120 chars, unique case-insensitive.
- At least one candidate id allowed? (Allow empty list initially— kit can be populated later). Document behavior.
- Candidate ids must exist; duplicates in list rejected.
- Rubric must exist; store its version & published flag at creation time.
- Cannot modify rubric_id post creation (attempt returns 409 / 422).
- If rubric is draft and later published externally, kit remains referencing same rubric record (no special action this iteration).

### Representation

- Response `DecisionKit` includes minimal embedded candidate info (id, name_original) to reduce round trips.
- Optional expand parameter `?expand=candidates,rubric` (future) — not in MVP.

### Error Semantics

- 404 if kit or referenced entity not found.
- 409 duplicate name.
- 422 invalid candidate list (duplicates or non-existent id).
- 409 attempt to change immutable rubric association (if added later in update logic).

## Impacted code

- New: `app/models/decision_kit_orm.py`
- New: `app/models/decision_kit_candidate_orm.py`
- New: `app/models/decision_kit.py` (Pydantic)
- New: `app/services/decision_kit_service.py`
- New: `app/routes/decision_kits.py`
- Existing: ensure candidates & rubrics modules imported prior to FK creation
- `app/main.py` register router
- README: add Decision Kit section

## Edge cases and risks

- Large candidate list ( >500 ) causing bulk insert performance hit — mitigate with simple length soft cap (document recommended <200).
- Deletion of candidate referenced by kit (FK restrict will block) — error surfaced as 409 mapped from IntegrityError.
- Deletion of rubric referenced by kit (should be prevented already if published; if draft and deleted, FK restrict prevents).
- Race: two concurrent creates with same name — rely on app-level normalization + uniqueness, return 409.
- Position ordering after candidate removal — re-normalize sequentially (0..n-1).

## Test plan

- Create kit with candidates success.
- Create kit duplicate name → 409.
- Create kit with non-existent candidate id → 422.
- Modify candidate list via PATCH (add/remove) persists and returns updated ordered list.
- Delete kit removes candidates association rows.
- Attempt to change rubric (if endpoint added) → 409 (not implemented now but ensure service guards internal misuse).
- Candidate deletion attempt while referenced → blocked (simulate and assert constraint error mapping).

## Migration/compat

- New tables only; no changes to existing rubric or candidate tables.
- Startup metadata create; no Alembic required for hackathon scope.

## Rollout

- No feature flag (immediate). Document endpoints and usage.
- Add to CHANGELOG / README.

## Links

- Relies on: Candidate feature (`copilot_planning/api/2025-09-16-candidate-materials/feature-plan.md`)
- Relies on: Rubric composition refactor (for stable rubric-candidate relationships)
