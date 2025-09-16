# Rubric Criterion Weights Enhancement

## Problem

Current rubric implementation stores criteria as an ordered list with optional weight embedded inline in a JSON blob. We need to formalize weights as a first-class concept so each rubric can explicitly assign a numeric weight to every associated criterion. This enables future scoring aggregation, consistent importance signaling, and validation (e.g., enforce positive numbers, optional normalization). Keeping weight inside generic JSON makes validation weaker, increases risk of inconsistent schema, and blocks richer queries later (e.g., identify high-weight criteria across rubrics).

## Goals (acceptance criteria)

- Each rubric MUST persist an explicit numeric weight for every criterion it references.
- Weight stored at the rubric–criterion association level (not in the base criteria record).
- API returns weights in rubric payloads in criteria order.
- Create/update endpoints validate: weight is a finite number > 0 (configurable lower bound; default strictly positive).
- If client omits weight for any criterion during create: server assigns default = 1.0 and returns that value.
- Optional: allow weight=0 only if feature flag `ALLOW_ZERO_WEIGHT` true (default false).
- Reject rubric creation/update if any weight is non-numeric, NaN, or negative (422).
- Backward compatibility: previously created rubrics (if any without weights) are auto-upgraded with default weight=1 on first read (no write unless updated/published again). (Only needed if legacy data detected.)

## Non-goals

- Total weight normalization / enforcing sum==1 (future scoring feature).
- Persisting weights in a join table (will remain JSON for this iteration, though schema sharpened).
- Historical weight version diffs or audit trail.
- UI implementation (handled in separate webapp feature plan).

## Design

### Data Model Approach (Incremental / Low-Risk)

Keep existing `criteria_json` TEXT column but standardize each entry shape to:

```json
{
  "criteria_id": <int>,
  "weight": <float>
}
```

Remove ambiguity of optional weight by always persisting it.

Add lightweight validation layer in service:

1. Parse payload list.
2. If any entry missing `weight`, set to default 1.0.
3. Validate each weight: `isinstance(weight, (int,float)) and isfinite(weight) and weight > 0` (or ≥0 when flag enabled).
4. Reject list containing duplicate `criteria_id`.
5. Preserve order exactly as submitted.

### Future Extensibility

- Later migration to dedicated table `rubric_criteria` with columns `(rubric_id, criteria_id, weight, position)` when search/aggregation complexity warrants it.
- Normalization or relative weight percentage computation can be layered without changing storage shape.

### API Changes

- Create (POST /rubrics): Require `criteria` array; each entry may optionally include `weight`; server ensures final persisted weight.
- Update (PUT/PATCH /rubrics/{id}): Same contract; if partial criteria update out of scope— full list replaced.
- Response schemas: Always show `weight` for each entry.
- OpenAPI docs updated to reflect non-optional weight in response model.

### Validation & Error Semantics

- Missing or empty `criteria` array: 400 (must have ≥1 criterion).
- Invalid criterion id: 400 (existing logic reused).
- Duplicate criterion ids: 422 (semantic error).
- Invalid weight (nan/inf/string/<=0 when zero not allowed): 422 with detail code `INVALID_WEIGHT` and index reference.

### Configuration

Environment variable(s):

- `ALLOW_ZERO_WEIGHT` (default false) – if true, accept weight==0 but still require non-negative.
- `DEFAULT_RUBRIC_WEIGHT` (default 1.0) – fallback assignment for omitted weights.

### Backward Compatibility Strategy

Detect legacy entries lacking `weight` (keys tested after JSON load). If found:

- Augment in-memory objects by adding `weight=DEFAULT_RUBRIC_WEIGHT` before returning.
- (Optional optimization) Defer persistence until a modifying operation occurs to avoid opportunistic writes.

## Impacted Code

- `app/models/rubric.py` (ensure Pydantic models reflect mandatory weight in response; create model allows optional weight for convenience)
- `app/services/rubric_service.py` (validation + default assignment + legacy upgrade pathway)
- `app/routes/rubrics.py` (possible refined error responses / status codes)
- `app/seed/seed_data.py` (ensure seeded rubric sets explicit weights)
- `README.md` (document weight semantics)
- Potential new: `app/config.py` (centralize env flag parsing) if not already present.

## Edge Cases & Risks

- Very large float values (overflow in later scoring) – mitigate by upper bound (e.g., cap at 1e6) and document.
- Passing string numbers ("1.5"): reject to avoid silent coercion.
- Negative zero (-0.0) treated as 0; treat as invalid unless zero allowed.
- Legacy rubric with mixed entries (some weighted, some not) – treat missing as needing default weight.
- JSON parse failure (corruption) – respond 500 with clear message; highlight that manual DB edits are unsupported.

## Test Plan

- Create rubric with explicit weights (happy path).
- Create rubric omitting weights → all default to 1.0 in response.
- Create rubric with weight=0 when flag disabled → 422.
- Create rubric with weight=0 when flag enabled → success.
- Create rubric with negative weight → 422.
- Create rubric with duplicate criteria → 422.
- Update rubric adding weights change → persists new weights.
- Legacy rubric read (simulate missing weights) returns weights all set to default without persistence.

## Migration / Compat

No schema migration required; JSON shape formally tightened. Optional data hygiene script (future) to backfill weights permanently.

## Rollout

- Add feature behind zero-config (defaults safe). Consumers immediately receive consistent `weight` field.
- Announce in README change log section.

## Open Questions

- Should upper bound be enforced (e.g., 100)? (Default: no hard cap; maybe warning later.)
- Should we allow decimal precision limit? (Not now.)

## Follow-ups (Post-Enhancement)

- Move to join table for analytics.
- Add normalization endpoint or client hint.
- Provide aggregate scoring endpoint using weights.

## Links

- Prior rubric feature plan: `copilot_planning/api/2025-09-15-rubric-support/feature-plan.md`
