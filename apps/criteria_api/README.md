# Criteria API (Python/FastAPI)

A RESTful API for managing criteria (name, description, definition) using Azure CosmosDB.

## Setup

1. Copy `.env.example` to `.env` and fill in your CosmosDB credentials.
2. Install dependencies:
   ```sh
   poetry install
   ```
3. Start the server:
   ```sh
   poetry run uvicorn app.main:app --reload
   ```

## Endpoints

- `GET /criteria` — List all criteria
- `GET /criteria/{id}` — Get a single criterion
- `POST /criteria` — Create a new criterion
- `PUT /criteria/{id}` — Update a criterion
- `DELETE /criteria/{id}` — Delete a criterion

### Rubrics & Criterion Weights

Rubrics group ordered criteria with per-criterion weights. Composition is stored in the `rubric_criteria` association table. All rubric responses always include a `weight` for each criterion. When creating or updating a rubric you may omit `weight` for an entry; the server will apply the default.

Environment variables (see `app/config.py`):

| Variable | Default | Description |
|----------|---------|-------------|
| `ALLOW_ZERO_WEIGHT` | `false` | If `true`, a weight of `0` is permitted; otherwise weights must be strictly > 0. |
| `DEFAULT_RUBRIC_WEIGHT` | `1.0` | Applied to any entry missing a weight on create/update. Must be > 0 unless zero allowed. |
| `MAX_RUBRIC_WEIGHT` | `1000000` | Upper bound for a single criterion weight. |

Validation errors return HTTP 422 with structured payloads, e.g.:

```json
{ "error": "INVALID_WEIGHT", "index": 0, "detail": "weight must be > 0" }
```

```json
{ "error": "DUPLICATE_CRITERIA", "criteria_id": "<uuid>", "index": 1 }
```

```json
{ "error": "WEIGHT_TOO_LARGE", "index": 2, "limit": 1000000 }
```

Key rubric endpoints:

- `GET /rubrics` — List rubrics (criteria returned in defined order)
- `GET /rubrics/{id}` — Retrieve rubric
- `POST /rubrics` — Create draft rubric
- `PUT /rubrics/{id}` — Update draft rubric (reorders/changes replace entire composition)
- `POST /rubrics/{id}/publish` — Publish a rubric (becomes immutable)
- `DELETE /rubrics/{id}` — Delete a draft rubric (cascades association rows)

Positions are reassigned on each update (PUT) based on the order supplied. Draft rubrics can be modified until published; after publishing a rubric becomes immutable (attempted changes return 409).

## Testing

- Run tests:

   ```sh
   pytest
   ```
