# Feature: Rubric Support (Criteria API)

## Summary

Add a Rubric resource that groups criteria with optional weights, enabling reusable evaluation sets with publish locking.

## Motivation

Users currently recreate ad-hoc lists of criteria. A rubric establishes a named, versionable bundle ensuring consistent evaluation templates and reducing manual repetition.

## Acceptance criteria

- Create rubric with unique name + description + list of criteria ids
- Duplicate name returns 409
- Update allowed only before publish
- Publish endpoint locks rubric (409 on further structural changes)
- Delete only allowed before publish
- Validation rejects unknown criteria ids & duplicate ids
- Optional weight persisted (0–1)
- Get/list endpoints return expected shapes; list filter by name substring

## Scope

In-scope: ORM model, CRUD endpoints, publish semantics, validation, optional expand=criteria.

## Out of scope

Auth, version branching, score aggregation, cloning, soft delete.

## Design overview

Store rubric in single table with JSON array of entry objects. Normalize name for uniqueness. Publish flips flag; future versions would be a new row.

## Impacted code

- models: `rubric_orm.py`, `rubric.py`
- services: `rubric_service.py`
- routes: `rubrics.py`
- main: router registration

## Test plan

Unit tests for create, duplicate, invalid criteria, publish lock, delete draft, weight bounds. Optional expand=criteria test.

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Race updating + publishing | Acceptable for hack scope; document |
| Large rubric payload performance | Enforce max criteria length |
| Stale criteria references later | Future cleanup job / cascade policy |

## Definition of Done

- All endpoints implemented & documented
- Tests pass (where added) and manual curl smoke test successful
- Docker build succeeds
- README/API docs updated with examples
