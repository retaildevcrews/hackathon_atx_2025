# Implementation Plan — Rubric Criterion Weights Enhancement

## Pre-flight

- [ ] Confirm existing rubric JSON structure in a few records (identify any entries missing weight).
- [ ] Decide env var defaults: `ALLOW_ZERO_WEIGHT=false`, `DEFAULT_RUBRIC_WEIGHT=1.0`.
- [ ] Confirm no dependant code assumes weight optional in responses (adjust UI plan accordingly when implemented later).
- [ ] Determine if any seeded rubric entries currently omit weight (update seeder).

## Data & Model Changes

- (No schema migration) Continue using `criteria_json` TEXT.
- Standardize entry shape to always include `weight`.
- Add config loader (new `config.py`) with:
  - `ALLOW_ZERO_WEIGHT: bool`
  - `DEFAULT_RUBRIC_WEIGHT: float`
  - Validation on load (DEFAULT_RUBRIC_WEIGHT > 0 unless zero allowed and equals 0).

## Service Layer Updates (`rubric_service.py`)

- Add helper `_normalize_and_validate_entries(entries, config)`:
  1. Iterate original list preserving order.
  2. If `weight` missing: assign default.
  3. Validate type (strict: `isinstance(weight, (int,float))`), finiteness, bounds ( >0 or >=0 if zero allowed), and upper cap (1e6) — reject above cap with code `WEIGHT_TOO_LARGE`.
  4. Track duplicates via set; raise on duplicate `criteria_id` with `DUPLICATE_CRITERIA`.
  5. Coerce ints to float explicitly for uniformity (e.g., `float(weight)`).
  6. Return sanitized list.
- On create/update: call helper before persistence.
- On read (get/list): detect legacy entries lacking `weight` — patch in memory with default (do NOT persist silently).

## Pydantic Schema Updates (`rubric.py`)

- Modify `RubricCriteriaEntry`:
  - `weight: float` (required in response model)
  - `RubricCriteriaEntryCreate` (if using separate) where `weight: Optional[float] = None`.
- Ensure OpenAPI shows weight required in returned objects.

## Routes (`rubrics.py`)

- Adjust create/update endpoint models to accept optional weight per entry but always respond with weight present.
- Map validation exceptions to 422 with structured JSON:
  - `{ "error": "INVALID_WEIGHT", "index": i, "detail": "must be > 0" }`
  - `{ "error": "WEIGHT_TOO_LARGE", "limit": 1000000 }`
  - `{ "error": "DUPLICATE_CRITERIA", "criteria_id": x }`
- Update existing weight related error mapping (if previously generic) to new schema.

## Seeder (`seed_data.py`)

- Ensure seeded rubric explicitly sets each weight (use 1.0 baseline unless domain-specific numbers preferred).
- Optional: add check to rewrite seed if legacy (skip if already weighted).

## Configuration (`config.py`)

```python
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    ALLOW_ZERO_WEIGHT: bool = False
    DEFAULT_RUBRIC_WEIGHT: float = 1.0
    MAX_RUBRIC_WEIGHT: float = 1_000_000.0

    @validator("DEFAULT_RUBRIC_WEIGHT")
    def validate_default(cls, v, values):
        allow_zero = values.get("ALLOW_ZERO_WEIGHT", False)
        if allow_zero and v == 0:
            return v
        if v <= 0:
            raise ValueError("DEFAULT_RUBRIC_WEIGHT must be > 0 unless zero allowed")
        return v

settings = Settings()
```

- Import `settings` in service.

## Error Handling Strategy

- Raise domain-specific exceptions (new custom types or ValueError with sentinel codes) → map in router.
- Maintain previous 409/400 semantics; use 422 for semantic validation errors.

## Testing

Unit tests (add new test module `tests/test_rubric_weights.py`):

- [ ] Create rubric explicit weights returns same floats.
- [ ] Create rubric missing weights returns defaults.
- [ ] Create rubric weight=0 when disallowed → 422.
- [ ] Create rubric weight=0 when allowed (patch env) → success.
- [ ] Negative weight → 422.
- [ ] Duplicate criteria → 422.
- [ ] Over max weight (>1e6) → 422.
- [ ] Legacy rubric (simulate missing weight entries) read returns augmented weights.
- [ ] Update rubric successfully changes weights prior to publish.
- [ ] Publish then attempt weight change → 409 (immutability still enforced).

## Documentation

- README: Add subsection "Rubric Criterion Weights" with request/response examples.
- Mention environment variables, validation rules, and default assignment behavior.
- Update previous rubric feature docs to remove wording implying weight is optional in response.

## Rollout Steps

1. Implement config + schema changes.
2. Update service + routes.
3. Adjust seed data.
4. Add tests & run locally.
5. Update README.
6. Rebuild container (docker compose) & smoke test via curl.

## Manual Smoke Test Checklist

- POST create with mixed entries (some weights omitted) → confirm defaults.
- GET list returns weights for all rubrics.
- PUT update modifies weight for a criterion.
- Publish then attempt update → blocked.
- Invalid submissions produce structured 422 payloads.

## Risks & Mitigations

- Hidden legacy data inconsistency → detection on read avoids crashes.
- Floating point precision concerns for future scoring → treat weight as arbitrary positive scalar; normalization later.
- Large payload size if many criteria → unchanged; still one JSON field.

## Follow-up (Future Iterations)

- Introduce join table for analytic queries.
- Add optional normalization endpoint.
- Add aggregated scoring endpoint using weights.
- CLI or admin script to permanently backfill missing weights.

## Completion Definition

- All tests green.
- Rubric responses always include weight.
- No seed or runtime rubrics without weight field.
- README updated and lint passes.
