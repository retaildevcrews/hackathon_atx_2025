# Implementation plan — Rubric Support

## Pre-flight

- [ ] Confirm SQLAlchemy is available (already in project dependencies)
- [ ] Decide if Alembic is needed now (skip; use metadata create)
- [ ] Confirm no breaking changes to criteria endpoints
- [ ] Validate naming regex & document in README section

## Implementation

- [ ] Add ORM model `rubric_orm.py` with fields (id, name_normalized, name_original, version, description, criteria_json, published, published_at, created_at, updated_at)
- [ ] Add Pydantic schemas `rubric.py`
- [ ] Add service `rubric_service.py` with: create, get_by_id, get_by_name, list, update, publish, delete
- [ ] Add validation helpers (name pattern, criteria existence, duplicate detection)
- [ ] Add router `rubrics.py` with endpoints (POST /rubrics, GET /rubrics, GET /rubrics/{id}, GET /rubrics/by-name/{name}, PUT /rubrics/{id}, POST /rubrics/{id}/publish, DELETE /rubrics/{id})
- [ ] Register router in `main.py`
- [ ] Ensure 409 on immutable operations (update/delete after publish)
- [ ] Implement optional `expand=criteria` (if time remains)

## Validation

- [ ] Unit tests: create, duplicate name, update draft, publish then update fail, delete draft
- [ ] Unit test: invalid criteria id rejection
- [ ] Unit test: weight out of bounds
- [ ] (Optional) integration: expand=criteria returns embedded criteria details

## Samples and documentation

- [ ] Add sample POST payload + response to API README (or root README rubric section)
- [ ] Document naming rules & publish semantics
- [ ] Provide curl examples for create, publish, list

## Rollout

- [ ] Add section to CHANGELOG or README
- [ ] Run docker compose build to verify no runtime errors
- [ ] Manual smoke test via curl for all endpoints
