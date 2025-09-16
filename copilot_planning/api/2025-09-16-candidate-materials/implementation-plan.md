# Implementation Plan — Candidate & Materials

## Pre-flight

- [ ] Add dependency: `azure-storage-blob` (verify in `pyproject.toml`)
- [ ] Define env vars: `AZURE_STORAGE_CONNECTION_STRING`, `CANDIDATE_MATERIALS_CONTAINER`, `MAX_CANDIDATE_FILE_SIZE_MB` (default 10), `ALLOWED_CANDIDATE_MIME_PREFIXES` (comma list)
- [ ] Confirm logging setup; no prints
- [ ] Decide checksum strategy (sha256 via incremental update during stream)

## Implementation

- [ ] ORM `candidate_orm.py` (CandidateORM)
- [ ] ORM `candidate_material_orm.py` (CandidateMaterialORM)
- [ ] Pydantic models `candidate.py` (CandidateCreate, Candidate, CandidateMaterial, CandidateMaterialListItem)
- [ ] Blob client wrapper `clients/blob_storage.py` with methods: `upload_stream(container, blob_path, data_stream, length, content_type, metadata)`, `download_stream(container, blob_path)`
- [ ] Config loader additions in existing settings (or new `config.py` block) for file size + allowed mime prefixes
- [ ] Service `candidate_service.py`: create/list/get (enforce unique normalized name)
- [ ] Service `candidate_material_service.py`:
  - upload_material(candidate_id, file: SpooledTemporaryFile or bytes, filename, content_type)
  - list_materials(candidate_id)
  - get_material(candidate_id, material_id) -> stream handle + metadata
  - optional delete_material
  - internal: validate size, type, uniqueness, compute checksum
- [ ] Routes `candidates.py`:
  - POST /candidates (JSON)
  - GET /candidates
  - GET /candidates/{id}
  - POST /candidates/{id}/materials (multipart/form-data)
  - GET /candidates/{id}/materials
  - GET /candidates/{id}/materials/{material_id}
  - DELETE /candidates/{id}/materials/{material_id} (optional)
- [ ] Wire router into `main.py`
- [ ] Add OpenAPI examples for upload + list

### Upload Flow Detail

1. Receive multipart file
2. Check candidate exists (404 if not)
3. Validate filename + type + size (read size from SpooledTemporaryFile or stream length; if unknown, buffer to measure with cap)
4. Compute sha256 while streaming to a temporary buffer or through tee into blob upload (opt: load into memory if <= threshold, else chunk)
5. Generate blob key `candidates/{candidate_id}/{uuid4}_{safe_filename}` (safe: lower, replace spaces, strip path separators)
6. Upload to blob with metadata (orig_filename, checksum)
7. Persist DB row inside transaction; on DB failure, attempt delete blob to avoid orphan
8. Return metadata response

### Download Flow Detail

1. Validate candidate + material association
2. Get blob path from DB row
3. Stream blob to client with `Content-Type` stored and header `Content-Disposition: attachment; filename="original_filename"`

## Validation

- [ ] Unit tests (service layer) for candidate create duplicate name
- [ ] Unit tests upload: success, duplicate filename, oversize, disallowed mime, zero-byte
- [ ] Integration test: round-trip download bytes equality
- [ ] Checksum test: stored checksum matches computed local one
- [ ] List materials ordering (most recent first)
- [ ] Delete material removes blob + row

## Samples and documentation

- [ ] README additions
- [ ] Example curl upload: multipart with `-F file=@sample.pdf`
- [ ] Example curl download: `-OJ` usage

## Rollout

- [ ] Add env var docs
- [ ] Provide fallback behavior: if storage not configured, endpoints return 503 with error JSON
- [ ] Docker compose: optionally add placeholder environment values

## Manual Smoke Test Checklist

- Create candidate → 201
- Upload pdf → 201 (verify size + checksum in response)
- List materials → returns uploaded
- Download → correct content-type and length
- Duplicate filename → 409
- Oversize file (simulate) → 413
- Disallowed mime → 415
- Delete material (if implemented) → 204 then list excludes

## Risks & Mitigations

- Memory usage on large files → enforce size limit early; stream to blob
- Slow blob operations → add short timeout / retry (2 attempts)
- Orphan blobs on failure → cleanup attempt with logged warning
- Unicode filenames → normalize and store original separately if needed (MVP: store as provided, sanitized for blob key)

## Completion Definition

- All endpoints implemented & documented
- Tests pass (unit + basic integration)
- No orphan blobs during normal flows (verified manually)
- README updated with usage section
