# Feature Plan: Generic Blob-backed File Ingestion Service (Azure Function + Blob Storage)

## Problem

Multiple product areas (candidate supporting materials today; potential future: rubric attachments, decision kit documents, evaluation exports) need to persist arbitrary small/medium binary artifacts (PDF, image, TXT, JSON, short media) securely and durably without inflating the relational/operational datastore. Current implementation for candidate materials stores raw bytes or pseudo-path metadata only, lacking a real blob backend and preventing larger (up to 10MB) files. Direct browser-to-blob approaches (SAS / SDK) are blocked by network constraints and we want to avoid distributing storage secrets or prematurely committing to a token issuance pattern. We need a reusable, domain-agnostic ingestion surface that any API route can call to offload file bytes into Azure Blob Storage using Managed Identity, returning normalized metadata (id, path, size, contentType, hash) that downstream feature-specific services can associate with their own domain models.

## Goals (acceptance criteria)

- Deliver a single Azure Function HTTP endpoint (upload) that is resource-agnostic: accepts a logical `contextType` (e.g., `candidate`, `rubric`, `decisionKit`, `evaluationExport`) and `contextId` plus file.
- Store file in Azure Blob Storage using Managed Identity (no shared keys, no SAS issuance) in a normalized container structure: `contextType/contextId/<fileId>_<sanitizedFilename>`.
- Return standardized metadata JSON: `fileId` (UUID v4), `contextType`, `contextId`, `originalFilename`, `contentType`, `size`, `sha256`, `blobPath`.
- Enforce configurable size limit up to 10MB (default 10MB) with streaming guard; reject > limit early with 413.
- Provide deterministic hashing (SHA256) computed while streaming (single pass) without fully buffering entire payload in memory beyond minimal chunk buffer.
- Support safe retry (idempotency) by returning a fresh `fileId` each attempt but allowing optional de-duplication future (hash-based) without breaking contract.
- Integrate initially only with candidate materials by adapting existing API route to call the generic service, without coupling generic function code to candidate domain logic.
- Produce structured logs including `contextType`, `contextId`, `fileId`, `blobPath`, `size`, `hash`, correlation/request identifiers.
- Provide minimal infrastructure description (Bicep high-level spec only in plan; detailed IaC & code out of scope for THIS iteration per feedback).
- Security phase 1: internal shared secret header + API-level auth; phase 2 placeholder for Entra OAuth2 client credentials or signed JWT from API.

## Non-goals

- Domain-specific validation inside the Function (remains in API layer).
- Direct browser upload (SAS / user delegation) in this iteration.
- Resumable or >10MB uploads.
- Malware scanning / content classification.
- Derivative generation (thumbnails, OCR, etc.).
- Public/signed download URL issuance.

## Design

### Architectural Overview
"Generic Upload Function" (GUF) provides a single HTTP endpoint. Domain services (initial: candidate materials API) validate domain-specific rules, then forward the file stream + context metadata to GUF. GUF authenticates the caller (internal shared secret header + optional correlation id), streams data to blob storage, computes metadata, and returns a normalized response.

### Data & Naming Model
- `contextType`: lowercase kebab or camel (validated against allow-list set via env `ALLOWED_CONTEXT_TYPES` e.g., `candidate,rubric,decisionKit,evaluationExport`).
- `contextId`: opaque string (UUID or domain identifier) – length & character whitelist enforced (e.g., `[A-Za-z0-9_-]{1,64}`).
- `fileId`: server-generated UUID v4.
- Blob path: `<contextType>/<contextId>/<fileId>_<sanitizedFilename>`; filename sanitized to remove path separators and control chars; truncation applied (e.g., max 120 chars before extension) to keep path length reasonable.

### Request / Response Contract (Function)
Request:
- Method: POST `/upload`
- Headers: `x-internal-upload-key: <raw>`, `content-type: multipart/form-data`
- Multipart fields:
  - `contextType`
  - `contextId`
  - `file`
Response 201 JSON:
```
{
  "fileId": "<uuid>",
  "contextType": "candidate",
  "contextId": "abc123",
  "originalFilename": "resume.pdf",
  "contentType": "application/pdf",
  "size": 345678,
  "sha256": "<hex>",
  "blobPath": "candidate/abc123/<fileId>_resume.pdf"
}
```
Errors: 400 (validation), 401 (auth), 413 (size), 415 (unsupported media type optionally), 500 (unexpected).

### Security Model (Phase 1)
- Internal secret (header) stored only in API and function configuration; hashed value (`INTERNAL_UPLOAD_KEY_SHA256`) compared constant‑time, raw shared secret never logged.
- Managed Identity for storage operations (no connection string/keys in code).
- Optional correlation header `x-correlation-id` propagated into logs.

### Observability (Minimal)
- Basic structured log per request: level INFO success `{event: upload, contextType, contextId, fileId, size, sha256_prefix}`; level WARN/ERROR on validation/auth failures with concise reason code. No metrics/telemetry in this iteration.

### Performance & Memory Strategy (10MB limit)
- Stream read in configurable chunk size (e.g., 256KB) accumulating size counter; abort once size > limit.
- Simultaneous hash computation and temporary in-memory buffer only for current chunk; no full buffering.

### Extensibility Hooks
- Future dedup: if `ENABLE_HASH_DEDUP=true` and a blob exists with same `sha256` under same context, optionally short-circuit and return existing metadata (out of scope now; design leaves space).
- Future direct browser support: plan alternate `mode=preauth` handshake returning one-use SAS token or function-signed ephemeral token.

### Integration Pattern for First Consumer (Candidate Materials)
- Candidate upload route morphs to: domain validate (candidate exists, file non-empty, business size limit), then call GUF; persist returned metadata (store `fileId`, `blobPath`, `sha256`, size, contentType) in material table.
- Domain remains free to apply additional tagging (e.g., marking file classification) without GUF changes.

### Configuration (Function)
- `STORAGE_ACCOUNT_URL`
- `BLOB_CONTAINER` (single generic container, e.g., `app-files`)
- `MAX_BYTES` (default `10485760` for 10MB)
- `INTERNAL_UPLOAD_KEY_SHA256`
- `ALLOWED_CONTEXT_TYPES`
- (Optional) `LOG_LEVEL`

### Backward Compatibility
Ignored for initial delivery (treat as greenfield for new uploads; legacy data handling deferred to consuming services outside this plan).

### Out of Scope in THIS Plan per Feedback
- Concrete directory/file scaffolding
- Detailed Bicep module decomposition (only high-level described below)
- React component implementation (documented as potential consumer sample)

## Impacted Areas (Conceptual)
- Candidate materials service (first adopter) – adapt to call generic uploader.
- Potential future: rubric attachments, decision kit docs, evaluation exports – minimal friction due to context abstraction.
- Documentation (`docs/azure-resources.md`) – add generic section “Generic Upload Function (GUF)”.
- Data model: candidate materials table gains columns `file_id`, `blob_path`, `sha256`, `content_type`, `size_bytes` (verify existing vs needed). Migration handled by domain team separately.

## Edge Cases & Risks
- Oversize file ( > limit ) – immediate 413; no partial blob committed (upload aborted before PutBlockList finalize or by skipping write once threshold hit).
- Unsupported `contextType` – 400 with machine-readable code `unsupported_context`.
- Path traversal attempts in filename – sanitized; log warning; proceed with safe filename.
- Duplicate uploads (rapid retry) – multiple distinct fileIds acceptable; dedup left for future.
- Orphan blobs (domain DB write fails after upload) – small risk accepted; future periodic orphan reaper (list + cross-check) can be added.
- Secret leakage risk – ensure secret only compared after length check & hashed form in config; encourage rotation process.
- Hash collision – SHA256 collision extremely unlikely; no mitigation required now.

## Test Plan (Focused)
Function Unit Tests:
- Happy path (<= limit) -> 201 and hash length 64.
- Oversize (> limit) -> 413 early termination.
- Missing/invalid contextType -> 400.
- Missing file part -> 400.
- Wrong secret -> 401.
- Boundary test exactly at 10MB -> success.

API Integration (first adopter – candidate materials):
- Successful upload persists returned metadata.
- Function auth failure -> propagated error; no DB row.

Negative: malformed multipart -> 400.

## Rollout Strategy
Simple deploy: once Function is available and API caller configured with secret + endpoint, start using for new candidate material uploads. No feature flag or phased gating.

## High-Level Infrastructure Notes (Reference Only)
- Storage Account (LRS), single container, Function App with system-assigned identity, role: Blob Data Contributor. Optional future: App Insights & Key Vault.

## Future Enhancements (Not in Scope)
- Direct browser pre-auth / SAS path.
- AV scanning pipeline (Event Grid trigger).
- Hash-based dedup + ref counting.
- Retention & lifecycle policies.
- CMK encryption option.

## Links / References
- Candidate materials current service: `apps/criteria_api/app/services/candidate_material_service.py` (first integration target)
- Documentation to update: `docs/azure-resources.md`
- Prior pseudo-path logic: same file/service above (baseline for migration notes)

---
Implementation details (code scaffolding, IaC, React component) intentionally excluded; this document only defines contract & minimal behavior.
End of simplified feature plan.
