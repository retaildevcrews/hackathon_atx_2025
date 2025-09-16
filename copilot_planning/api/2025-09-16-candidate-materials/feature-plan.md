# Candidate & Candidate Materials Feature

## Problem

Evaluation workflows need a way to associate a set of source documents (resumes, portfolios, specs, transcripts, prior work artifacts) with an entity under evaluation. Currently, the system has no concept of a "candidate" nor a standardized mechanism for storing and retrieving related materials. Ad-hoc file handling blocks consistent ingestion, indexing, and rubric-based evaluation.

## Goals (acceptance criteria)

- Create a Candidate with unique name (case-insensitive) and description.
- Attach one or more documents (candidate materials) to a candidate via API upload.
- Retrieve list of materials metadata (filename, size, content_type, uploaded_at, storage_url or blob key).
- Download an individual material via secure API endpoint (streamed response).
- Prevent duplicate filenames per candidate (either reject or auto-version; MVP: reject with 409).
- Enforce max single file size limit (configurable, default 10MB) and total candidate storage cap (configurable, soft limit warning in response header or metadata field).
- Delete a material (draft state assumption; no complex retention semantics) — optional stretch.
- OpenAPI reflects new schemas and endpoints.

## Non-goals

- Complex permissions / RBAC.
- Virus / malware scanning (placeholder for future).
- Automatic text extraction / embedding (future ingestion pipeline step).
- Public unauthenticated URLs (all access via API auth context — placeholder; current hackathon may run open/local).
- Versioning of materials beyond simple name uniqueness rejection.

## Design

### Data Model

- Table `candidates`:
  - id (PK)
  - name_original (text)
  - name_normalized (text, unique index lower(name_original))
  - description (text, optional)
  - created_at, updated_at
- Table `candidate_materials`:
  - id (PK)
  - candidate_id (FK -> candidates.id, cascade delete)
  - original_filename (text)
  - content_type (text)
  - size_bytes (int)
  - blob_path (text)  -- `candidates/{candidate_id}/{uuid4}_{sanitized_filename}`
  - uploaded_at (timestamp)
  - checksum_sha256 (char(64)) (optional for integrity; stored if provided / computed)
  - UNIQUE(candidate_id, original_filename)

Optional future fields: `extracted_text_path`, `embedding_vector_ref`.

### Storage

- Azure Blob Storage container (env var: `CANDIDATE_MATERIALS_CONTAINER`).
- Use connection string or managed identity (hackathon: connection string env var `AZURE_STORAGE_CONNECTION_STRING`).
- Upload: stream file to blob; compute size + optional sha256.
- Download: server streams blob to client with correct content-type and disposition header.

### API Endpoints (prefix `/candidates`)

- POST `/candidates` → create candidate (JSON body)
- GET `/candidates` → list candidates (basic pagination ?limit & ?offset)
- GET `/candidates/{id}` → candidate detail incl. material count
- POST `/candidates/{id}/materials` → multipart/form-data (field: `file`) upload
- GET `/candidates/{id}/materials` → list materials metadata
- GET `/candidates/{id}/materials/{material_id}` → download (stream)
- DELETE `/candidates/{id}/materials/{material_id}` → (optional stretch) remove both DB row + blob

### Validation

- Candidate name required, non-empty, trimmed, <= 120 chars.
- Reject duplicate candidate name (409).
- File upload: enforce size <= MAX_FILE_SIZE_BYTES (env; default 10MB).
- Reject unsupported content_types (configurable allowlist: pdf, txt, docx, md, png, jpg; env `ALLOWED_CANDIDATE_MIME_PREFIXES`).
- Reject zero-length uploads.

### Security & Integrity (MVP minimal)

- Basic logging of upload (candidate_id, filename, size, checksum prefix).
- Return opaque material id; blob path hidden (except maybe in internal admin tools).
- Include checksum in metadata to aid future tamper detection.

### Error Conditions

- 404 if candidate not found.
- 409 duplicate candidate name or duplicate filename per candidate.
- 413 payload too large for file.
- 415 unsupported media type.
- 422 invalid name / malformed multipart.

### OpenAPI / Schemas

- Pydantic: CandidateCreate, Candidate, CandidateMaterial, CandidateMaterialListItem.
- Response for upload returns material metadata (id, filename, size, content_type, uploaded_at, checksum).

## Impacted code

- New: `app/models/candidate_orm.py`
- New: `app/models/candidate_material_orm.py`
- New: `app/models/candidate.py` (Pydantic)
- New: `app/services/candidate_service.py`
- New: `app/services/candidate_material_service.py`
- New: `app/routes/candidates.py`
- Possibly new: `app/clients/blob_storage.py` (Azure Blob wrapper)
- `app/main.py` register router
- `README.md` update (API usage examples)
- `docker-compose.yml` ensure env vars present (if not already)

## Edge cases and risks

- Large simultaneous uploads → memory pressure (use Streaming upload API from Azure SDK; chunking if needed).
- Filename collisions with differing case (treat case-insensitive uniqueness).
- Blob storage transient failures → implement simple retry (exponential 2 attempts) or fail fast; log.
- Partial failure after blob upload but before DB commit (cleanup orphan blob on exception path).
- Download of missing blob (DB row present) → return 502/500 and optionally mark material as corrupted (future improvement).

## Test plan

- Create candidate success + duplicate name conflict.
- Upload material success (validate metadata fields populated).
- Duplicate filename conflict.
- Reject oversize file (simulate by content-length or generated bytes).
- List materials returns uploaded item.
- Download returns exact bytes (round-trip integrity test with checksum).
- Delete material removes blob + row (if implemented).
- Unsupported MIME type rejected.

## Migration/compat

- New tables created via metadata; no impact to existing rubric/criteria features.
- Optional stub if blobs not configured: upload endpoint returns 503 with actionable message.

## Rollout

- Add README section with curl examples (create candidate, upload file, list, download).
- Log counts of uploads per candidate at INFO level.
- Provide env var defaults in `.env.example` (if such file maintained) or docs.

## Links

- Azure SDK for Python (blobs): <https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python>
- Related future ingestion pipeline (not yet implemented)
