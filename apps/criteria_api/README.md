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

## Core Criteria Endpoints

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

### Candidate Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/candidates` | List candidates (newest first) |
| POST | `/candidates` | Create candidate `{ name, description, decisionKitId? }` (unique name; optional immediate association) |
| GET | `/candidates/{candidateId}` | Get candidate |
| POST | `/candidates/{candidateId}/materials` | Upload material (multipart form field `file`) |
| GET | `/candidates/{candidateId}/materials` | List material metadata |
| GET | `/candidates/{candidateId}/materials/{materialId}` | Get single material metadata |
| DELETE | `/candidates/{candidateId}/materials/{materialId}` | Delete material (metadata + underlying blob placeholder) |
| DELETE | `/candidates/{candidateId}` | Delete candidate (hard delete; cascades materials & kit associations) |

### Material Validation

Currently enforced:

- Non-empty file (size > 0)
- Maximum size (see env var below)
- Basic MIME presence (client provided) – can be tightened later

### Candidate Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CANDIDATE_MAX_MATERIAL_BYTES` | `1048576` (1MB) | Max allowed upload size. |
| `CANDIDATE_ALLOWED_MIME_PREFIXES` | `text/,application/` | Comma-separated list of MIME prefixes accepted. (If not enforced yet, planned) |

### Example (PowerShell friendly)

```pwsh
$body = @{ name = 'Jane Doe'; description = 'Staff Engineer' } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/candidates -Method Post -ContentType 'application/json' -Body $body
```

Upload a material:

```bash
curl -X POST http://localhost:8000/candidates/<CID>/materials \
   -F "file=@README.md;type=text/plain"
```

Duplicate candidate name returns HTTP 400 with JSON `{ "error": "DUPLICATE_CANDIDATE" }` (mapped internally from a uniqueness violation).

### Candidate Creation With Decision Kit Association

Including `decisionKitId` in the POST body will append the new candidate to the specified decision kit at the next available position (only if the kit status is `OPEN`). Example:

```bash
curl -s -X POST http://localhost:8000/candidates \
   -H "Content-Type: application/json" \
   -d '{
      "name": "Vendor A",
      "description": "Primary vendor",
      "decisionKitId": "<DECISION_KIT_ID>"
   }'
```

Failures:
| Condition | Response |
|-----------|----------|
| Unknown decisionKitId | 400 `{ "detail": "Invalid decision kit id" }` |
| Decision kit not OPEN | 400 `{ "detail": "Decision kit not open for modification" }` |

### Decision Kits & Candidate Names

Decision kit responses embed associated candidates via an association table; each embedded object includes `candidateId` and a dynamically populated `candidateName` (no duplicate denormalized column persisted). This avoids sync drift and ensures future name edits reflect immediately.

Deleting a candidate removes its materials and any decision kit associations; decision kits remain but their candidate list shrinks and positions are not auto-compacted (a future enhancement may re-normalize positions on delete if required by UI).


## Testing

- Run tests:

   ```sh
   pytest
   ```
