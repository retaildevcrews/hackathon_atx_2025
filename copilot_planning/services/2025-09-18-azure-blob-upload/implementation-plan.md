# Implementation Plan — Generic Blob-backed File Ingestion Service

This plan enumerates concrete, verifiable steps to implement the generic Azure Function upload service and integrate the first consumer (candidate materials) at a minimal scope (no feature flags, minimal observability).

---
## Pre-flight

- [ ] Confirm Python runtime version for Function (target 3.11) and that repo tooling supports it (adjust if constraints found).
- [ ] Identify and list external dependencies (azure-functions, azure-identity, azure-storage-blob, python-multipart or starlette/form parsing if needed). Add to dedicated `requirements.txt` for the Function project (not global).
- [ ] Verify no existing IaC conflicts (none present) – choose path for initial manual deployment vs future Bicep (document only, code later).
- [ ] Define environment variables & contract (STORAGE_ACCOUNT_URL, BLOB_CONTAINER, MAX_BYTES, INTERNAL_UPLOAD_KEY_SHA256, ALLOWED_CONTEXT_TYPES, LOG_LEVEL) – document defaults.
- [ ] Decide hash algorithm (SHA256) and chunk size (256KB) – record constants.
- [ ] Confirm candidate materials domain model changes required (new columns or re-use existing fields). Capture migration delta (if needed) but not executed in this iteration per narrowed scope.
- [ ] Security secret handling approach: store raw secret only in API; hash pre-provisioned into Function config.

## Implementation

- [ ] Create function project directory scaffold (no code yet in plan execution): `apps/generic_upload_function/` with placeholders: `host.json`, `local.settings.json.example`, `requirements.txt`.
- [ ] Implement HTTP trigger function `upload/__init__.py`:
	- Parse multipart form fields: contextType, contextId, file.
	- Validate: non-empty, allowed contextType, size streaming check, <= MAX_BYTES.
	- Stream file -> compute sha256, accumulate size, abort if limit exceeded.
	- Generate fileId (UUID4), sanitize filename, construct blob path.
	- Obtain blob client (using DefaultAzureCredential / Managed Identity in cloud; for local dev fall back to connection string if present).
	- Upload stream (single call since size ≤ 10MB) or staged blocks if size threshold exceeded for reliability.
	- Return JSON metadata.
- [ ] Add centralized error handling mapping to 4xx codes (ValidationError, AuthError) and 500 fallback.
- [ ] Implement logging helper (structured dict -> json string) using `logging.getLogger(__name__)`.
- [ ] Add configuration loader (pull env vars, parse numeric limit, split ALLOWED_CONTEXT_TYPES).
- [ ] Add simple filename sanitizer utility (strip path separators, control chars, collapse whitespace, enforce length limit).
- [ ] Implement shared secret verification (constant-time compare of sha256 hex digest).
- [ ] Add minimal retry (optional) for transient blob upload error (e.g., 3 attempts with exponential backoff) – log on retry.
- [ ] In API layer (candidate materials service): add HTTP client wrapper using `requests` or `httpx` (choose existing dependency style in repo – if none, prefer `httpx` for timeout support) to call Function endpoint. (Note: actual code may be deferred if project owner wants; include stub plan.)
- [ ] Replace pseudo path generation in candidate service with call to uploader client (if integration included in this iteration) OR add TODO marker referencing implementation plan step.

## Validation

- [ ] Unit tests (Function):
	- Happy path small file (text/plain) returns 201, includes sha256.
	- Oversize file (limit+1 byte) -> 413.
	- Missing contextType -> 400.
	- Unsupported contextType -> 400.
	- Missing file part -> 400.
	- Wrong secret -> 401.
	- Boundary at EXACT limit (10MB) -> success.
- [ ] Unit tests (utilities): filename sanitizer, hash streaming function (deterministic), secret verification.
- [ ] Contract tests (API wrapper -> mocked function response) verifying translation of errors and metadata persistence call arguments.
- [ ] (Optional) Integration test with Azurite (if added) flagged `@skip` unless env `USE_AZURITE=1`.
- [ ] Lint/type check (if mypy/ruff/flake8 standards present) – add ignore entries only if necessary.

## Samples and documentation

- [ ] Provide example HTTP request (curl) in `docs/azure-resources.md` update section “Generic Upload Function”.
- [ ] Add a sample JSON response snippet to same doc.
- [ ] Add quickstart steps (local run with func tools + Azurite or connection string) to doc.
- [ ] (Optional) Add minimal React component usage outline (NOT implemented) referencing existing API route as adapter.

## Rollout

- [ ] Document manual deployment steps (az cli: create storage account, enable identity, assign role, set app settings) – no feature flag.
- [ ] Record required secret hashing command (e.g., `echo -n $SECRET | openssl dgst -sha256`).
- [ ] Update `docs/azure-resources.md` with environment variable table.
- [ ] Add note about future enhancements (direct browser path, dedup) and that telemetry/metrics intentionally deferred.

---
## Detailed Task Breakdown & Ordering
1. Pre-flight dependency + env var documentation.
2. Create function scaffold files (empty placeholders).
3. Implement config loader & constants.
4. Implement sanitizer + hashing stream utility.
5. Implement auth (secret verification) module.
6. Implement upload function (parsing + validation + streaming + blob write + response).
7. Add logging & error mapping.
8. Write unit tests for utilities & core function logic (mock blob client).
9. Implement API uploader client stub & adjust candidate service (if in scope now).
10. Add documentation updates & sample request.
11. Add integration (optional Azurite) test harness.
12. Final review & checklist completion.

## Risks & Mitigations
- Multipart parsing memory spikes: ensure chunked read + size counter; reject early.
- Secret misconfiguration: add startup log verifying `INTERNAL_UPLOAD_KEY_SHA256` present.
- Incorrect contextType allow-list causing future adoption friction: document how to append and keep validation table-based.
- Blob path collisions: use UUID fileId prefix; extremely low risk.
- Local vs deployed credential differences: fallback logic clear & documented; explicit warning log if using development connection string instead of managed identity.

## Acceptance Criteria Mapping
Goal (generic endpoint) -> Steps 2–6.
Hash & metadata integrity -> Steps 4,6 tests in Validation.
10MB streaming limit -> Steps 4,6 with tests oversize/boundary.
Minimal logging -> Step 7.
First consumer integration path -> Step 9.

---
Completion of this plan yields: Function code + tests + docs updates + API integration stub ready for expansion.
