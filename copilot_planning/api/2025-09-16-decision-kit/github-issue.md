# GitHub Issue: Decision Kit

## Title

Create Decision Kit entity bundling rubric and candidates

## Summary

Add a Decision Kit construct that binds a rubric (with version snapshot) and a set of candidates for consistent evaluation sessions.

## Motivation

Ensures evaluation consistency by preventing silent rubric drift and providing a stable candidate set reference for downstream scoring/report generation (future). Simplifies orchestration and auditing.

## Acceptance criteria

- POST create kit with name, rubric_id, candidate_ids[]
- GET list kits (filter by name substring)
- GET kit detail returns rubric snapshot fields + ordered candidates
- PATCH candidates replace list (reorder + add/remove)
- DELETE kit (OPEN status only) cascades candidate links
- Name uniqueness enforced (case-insensitive)
- Duplicate candidate ids rejected with 422

## Scope

Included:

- ORM models (kit + kit candidates)
- Service + routes
- Basic validation & ordering

Excluded:

- Status transitions beyond OPEN
- Report generation / scoring
- Rubric cloning or embedding full rubric JSON

## Out of scope

- Historical versions of kits
- Candidate or rubric soft deletes
- Advanced pagination or filtering

## Design overview

- decision_kits table stores rubric version + published snapshot
- decision_kit_candidates table stores candidate links + position
- Immutable rubric association after creation
- Candidate list replace operation for simplicity

## Impacted code

- `app/models/decision_kit_orm.py`
- `app/models/decision_kit_candidate_orm.py`
- `app/models/decision_kit.py`
- `app/services/decision_kit_service.py`
- `app/routes/decision_kits.py`
- `app/main.py`
- `README.md`

## Test plan

- Create kit success
- Duplicate name conflict
- Non-existent candidate id failure
- Candidate list update (reorder + removal)
- Delete kit cascades associations
- Attempt reorder on missing kit 404

## Risks and mitigations

- Large candidate lists → documented guidance
- Race on concurrent updates → last write wins, acceptable
- FK constraint failures → map to 409 for delete attempts of referenced entities

## Definition of Done

- Endpoints operational & documented
- Tests green for core flows
- README updated with examples
