# GitHub Issue: Candidate & Candidate Materials

## Title

Add Candidate entity with blob-stored materials (upload/download APIs)

## Summary

Introduce a Candidate model with associated document materials stored in Azure Blob Storage. Provide REST endpoints to create candidates, upload materials, list materials, and download individual files.

## Motivation

Evaluation workflows need consistent attachment and retrieval of source documents for rubric-based and AI-driven analysis. Centralizing storage and metadata enables downstream ingestion (OCR, embedding) and prevents ad-hoc file handling.

## Acceptance criteria

- Create candidate (unique name) endpoint.
- Upload material (multipart) with size/type validation.
- List materials returns metadata (id, filename, size, content_type, uploaded_at, checksum).
- Download material streams original bytes with correct headers.
- Duplicate candidate name or filename returns 409.
- Oversize upload returns 413; unsupported type returns 415.

## Scope

Included:

- ORM models, services, routes
- Azure blob wrapper client
- Basic validation & checksum

Excluded:

- Text extraction / embedding
- Public links / signed URL generation
- Versioning beyond duplicate reject

## Out of scope

- Advanced auth/RBAC
- Malware scanning
- Content moderation

## Design overview

- Two tables: `candidates`, `candidate_materials` with UNIQUE(candidate_id, original_filename).
- Blob path scheme: `candidates/{candidate_id}/{uuid4}_{sanitized}`.
- Streaming upload + sha256 checksum.
- Configurable limits and mime allowlist via env vars.

## Impacted code

- `app/models/candidate_orm.py`
- `app/models/candidate_material_orm.py`
- `app/models/candidate.py`
- `app/services/candidate_service.py`
- `app/services/candidate_material_service.py`
- `app/clients/blob_storage.py`
- `app/routes/candidates.py`
- `app/main.py`
- `README.md`

## Test plan

- Candidate create + duplicate
- Upload success + duplicate filename
- Oversize rejection, unsupported type rejection
- List materials shows upload
- Download matches original bytes
- (Optional) delete removes row + blob

## Risks and mitigations

- Blob orphaning → cleanup on DB failure
- Large file memory use → streaming implementation
- Unsupported mime proliferation → configurable allowlist

## Definition of Done

- Endpoints implemented + documented
- Tests pass for core flows
- README updated with curl examples
