# Implementation Plan — Decision Kit

## Pre-flight

- [ ] Confirm candidates feature and rubric models available (importable)
- [ ] Decide if we enforce rubric must be published (MVP: allow draft; snapshot version + published flag)
- [ ] Confirm no need for feature flag
- [ ] Add indexes: decision_kits.name_normalized, decision_kit_candidates (decision_kit_id, position)

## Implementation

- [ ] ORM `decision_kit_orm.py` (DecisionKitORM)
  - relationship: `candidates_assoc = relationship("DecisionKitCandidateORM", back_populates="decision_kit", cascade="all, delete-orphan", order_by="DecisionKitCandidateORM.position")`
- [ ] ORM `decision_kit_candidate_orm.py`
- [ ] Pydantic `decision_kit.py` models:
  - DecisionKitCandidateRef (id, candidate_id, candidate_name, position)
  - DecisionKitCreate (name, description?, rubric_id, candidate_ids[])
  - DecisionKitUpdateCandidates (candidate_ids[])
  - DecisionKit (id, name, description, rubric_id, rubric_version, rubric_published, status, candidates[])
- [ ] Service `decision_kit_service.py` with functions:
  - create_decision_kit(...)
  - get_decision_kit(id)
  - list_decision_kits(filter_name?)
  - update_candidates(kit_id, candidate_ids)
  - delete_decision_kit(kit_id)
  - internal helpers: normalize_name, validate_candidate_ids, load_rubric_snapshot
- [ ] Routes `decision_kits.py` mapping endpoints, error translation
- [ ] Register router in `main.py`
- [ ] Add logging (INFO create/delete; DEBUG candidate updates)

### Candidate Update Logic

1. Fetch kit (404 if missing)
2. Ensure status == OPEN
3. Validate candidate ids existence & uniqueness
4. Delete existing candidate association rows
5. Insert new rows with incremented positions
6. Return updated kit DTO

### DTO Assembly

- Query kit with joined candidate associations and candidate table for names (either join or per-id fetch; prefer single joined query)
- Map to Pydantic, preserving order by position

## Validation

- [ ] Unit: create successful
- [ ] Unit: duplicate name 409
- [ ] Unit: non-existent candidate id 422
- [ ] Unit: update candidates reorder and removal
- [ ] Unit: delete kit cascades rows
- [ ] Unit: attempt to update non-existent kit 404
- [ ] Unit: attempt to change rubric (not exposed) guarded in service (simulate misuse) → raises

## Samples and documentation

- [ ] README section: Creating a Decision Kit
- [ ] Example JSON payloads (create, update candidates)
- [ ] curl examples for create/list/get/update/delete

## Rollout

- [ ] Add entry to CHANGELOG (if present)
- [ ] Rebuild containers and smoke test endpoints

## Manual Smoke Test Checklist

- Create kit with 2 candidates
- List kits contains new kit
- Get kit returns candidates in order
- Update candidates (swap order + add new) persists
- Delete kit removes it from list and cascades rows

## Risks & Mitigations

- Large candidate list performance → acceptable MVP; consider pagination or lazy load later
- Race conditions on concurrent candidate updates → replacing rows means last write wins (document)
- Future status transitions → schema allows status field extension

## Completion Definition

- Decision Kit endpoints operational and documented
- All tests green
- No integrity violations (FK constraints enforce referential integrity)
