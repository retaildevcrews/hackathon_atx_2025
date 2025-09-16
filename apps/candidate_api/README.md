# Candidate API

FastAPI service for managing candidates and their uploaded "materials" (e.g. resumes, documents) using:

- Azure Cosmos DB (candidates + candidate materials containers)
- Azure Blob Storage (binary material storage; falls back to disabled:// URLs if no connection string configured)
- Shared utility layer (`apps/shared_utils`) for Cosmos & Blob abstractions

## Features
- Create & list candidates with uniqueness on normalized name
- Upload, list, retrieve metadata, and delete candidate materials
- Validates material size and MIME type prefix (configurable)
- Partitioned Cosmos design: `/id` for candidates, `/candidateId` for materials
- Graceful blob fallback when storage not configured (still records metadata)

## Running (Locally)
Poetry install (installs path dependency on `shared_utils`):

```bash
cd apps/candidate_api
poetry install
poetry run uvicorn app.main:app --reload --port 8002
```

Or via Docker Compose from repo root:
```bash
docker compose up candidate_api
```
Visit: http://localhost:8002/docs

## Testing
Tests use in-memory dummy repositories & blob client (no network calls):
```bash
cd apps/candidate_api
poetry run pytest -q
```

## Shared Utilities
The service consumes `shared_utils.cosmos` and `shared_utils.blob`:
- `candidate_repository()` & `material_repository()` create containers with appropriate partition keys.
- `get_blob_client()` returns a singleton wrapper; if storage is not configured uploads return a `disabled://` URL.

## API Summary
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health/info message |
| GET | `/candidates/` | List candidates |
| POST | `/candidates/` | Create candidate `{name, description}` |
| GET | `/candidates/{candidateId}` | Get candidate |
| POST | `/candidates/{candidateId}/materials` | Upload material (multipart file) |
| GET | `/candidates/{candidateId}/materials` | List materials (metadata) |
| GET | `/candidates/{candidateId}/materials/{materialId}` | Get material metadata |
| DELETE | `/candidates/{candidateId}/materials/{materialId}` | Delete material metadata & blob |

## Error Handling
- 400 for duplicate candidate name, invalid file (empty, size, MIME)
- 404 when candidate or material not found

## Logging
Service emits structured INFO / WARNING logs for create operations & validation failures. Extend or centralize logging as needed.

## Quick Start: Sample curl Commands

Health & docs:
```bash
curl http://localhost:8002/healthz
curl http://localhost:8002/
```

Create a candidate:
```bash
curl -X POST http://localhost:8002/candidates/ \
	-H "Content-Type: application/json" \
	-d '{"name": "Jane Doe", "description": "Staff Engineer"}'
```

List candidates:
```bash
curl http://localhost:8002/candidates/
```

Get a candidate:
```bash
CID=<candidate-id>
curl http://localhost:8002/candidates/$CID
```

Upload a material (text file example):
```bash
CID=<candidate-id>
curl -X POST http://localhost:8002/candidates/$CID/materials \
	-F "file=@README.md;type=text/plain"
```

List materials for a candidate:
```bash
CID=<candidate-id>
curl http://localhost:8002/candidates/$CID/materials
```

Get a material's metadata:
```bash
CID=<candidate-id>
MID=<material-id>
curl http://localhost:8002/candidates/$CID/materials/$MID
```

Delete a material:
```bash
CID=<candidate-id>
MID=<material-id>
curl -X DELETE http://localhost:8002/candidates/$CID/materials/$MID
```

Duplicate candidate (expect 400):
```bash
curl -X POST http://localhost:8002/candidates/ \
	-H "Content-Type: application/json" \
	-d '{"name": "Jane Doe", "description": "Duplicate Test"}' -i
```

Oversized / invalid MIME uploads will return 400 with a descriptive message.

> Tip (PowerShell): replace `CID=<candidate-id>` lines with `$CID='<value>'` and use `$CID` variable syntax.