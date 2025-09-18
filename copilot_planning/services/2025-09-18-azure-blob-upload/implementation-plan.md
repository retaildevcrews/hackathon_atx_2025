# Implementation Plan — Generic Blob-backed File Ingestion Service (Updated Reality Snapshot)

This plan enumerates concrete, verifiable steps to implement the generic Azure Function upload service and integrate the first consumer (candidate materials) at a minimal scope (no feature flags, minimal observability).

---
## Pre-flight (Actual Status)

- [x] Python runtime version selected: 3.11 (function code written accordingly).
- [x] Dependencies captured in `apps/functions/requirements.txt` (azure-functions, azure-identity, azure-storage-blob, python-multipart, etc.).
- [x] IaC path chosen and implemented (Bicep templates instead of manual only; includes Function, Web App, Managed Identity, App Insights, role assignment two-pass pattern).
- [x] Environment variables defined: `STORAGE_ACCOUNT_URL`, `BLOB_CONTAINER`, `MAX_BYTES`, `INTERNAL_UPLOAD_KEY_SHA256`, `ALLOWED_CONTEXT_TYPES`, `LOG_LEVEL`, plus added `DISABLE_INTERNAL_UPLOAD_AUTH` (demo bypass flag) post initial design.
- [x] Hash algorithm SHA256; stream chunk size 256KB implemented.
- [~] Candidate materials integration deferred (no model changes performed; integration stub not yet implemented) – tracked as future enhancement.
- [x] Secret handling via SHA256 of raw secret (pre-hashed value configured). Demo bypass flag added later for frictionless local usage.

## Implementation (Planned vs Done)

Legend: [x] done, [ ] not started, [~] partial/deferred

- [x] Scaffold created under `apps/functions/` (includes `requirements.txt`, Dockerfile; `host.json` implicit via Functions tooling to be added if required later).
- [x] HTTP trigger function implemented (`upload/function_app.py` rather than `__init__.py` for clarity).
  - [x] Multipart parsing (manual boundary parsing kept minimal; using python-multipart library).
  - [x] Validation (contextType allow-list, size enforcement during streaming, required fields).
  - [x] Streaming SHA256 + size accumulation (abort on > MAX_BYTES).
  - [x] UUID filename prefix + sanitizer.
  - [x] Blob client via `DefaultAzureCredential` (expect MI in Azure; local dev uses Azurite / connection string path if set).
  - [x] Single-shot upload (size ≤ 10MB) – no block staging needed.
  - [x] JSON response (blobPath, sha256, size).
- [x] Centralized error mapping (custom exceptions -> appropriate status codes) implemented in function handler logic.
- [x] Logging helper implemented (`core/logging_utils.py`).
- [x] Config loader (`core/config.py`).
- [x] Filename sanitizer (`core/sanitizer.py`).
- [x] Shared secret verification (`core/secret.py`) with later addition of bypass flag.
- [ ] Retry logic for transient blob errors (not implemented; considered low priority for <=10MB uploads; future enhancement candidate).
- [ ] Candidate service HTTP client integration (deferred; not in current scope). No TODO yet inserted; recommend adding backlog item.

Additional (not in original Implementation list):
- [x] Auth bypass flag (`DISABLE_INTERNAL_UPLOAD_AUTH`) for demo scenarios.
- [x] Containerization via Dockerfile and usage docs.
- [x] Bicep IaC for Function + Web App + Managed Identity + App Insights + two-pass role assignment pattern.

## Validation (Current State)

- Utilities tests present: sanitizer, secret (added bypass test), streaming logic.
- Endpoint-level HTTP tests (status codes, boundary conditions) NOT yet implemented (gap vs plan).
- No contract tests (client integration deferred).
- No explicit Azurite integration test harness yet (could be added with pytest marker later).
- Lint/type checks not configured in this folder (future improvement if repo adopts ruff/mypy baseline).

Gaps:
- Need tests for: oversize file rejection, boundary at limit, missing/invalid fields, wrong secret (partially covered by `test_secret.py` but not full request path).
- Suggest adding minimal FastPath tests using Functions test host or refactoring core logic into a pure function to unit test validations.

## Samples and Documentation (Status)

- [x] Example curl request added in function `README.md`.
- [ ] Not yet added to `docs/azure-resources.md` (only local README contains details) — action needed for central docs parity.
- [x] Quickstart (local run, Docker, compose) documented.
- [ ] JSON response example snippet absent (could add to docs for clarity).
- [ ] React component usage outline not added (optional, still deferred).

## Rollout (Actual)

- [x] IaC Bicep provides automated deployment path (supersedes manual-only approach). Two-pass role assignment documented in infra README.
- [ ] Central docs (`docs/azure-resources.md`) still need environment variable table sync (currently only in function README + infra README for partial set).
- [ ] Secret hashing command example not yet documented (should add for clarity; e.g. PowerShell & bash variants).
- [x] Future enhancements noted in README (scanning, metadata, SAS evolution).
- [x] Telemetry intentionally minimal; App Insights resource provisioned but not deeply instrumented.

---
## Revised Task Breakdown (Reflecting Reality & Next Steps)
Completed:
1. Dependencies & env vars documented (local README).
2. Scaffold + config loader + utilities (sanitizer, streaming, secret verification).
3. Upload function core logic + logging + error handling.
4. Basic tests (utilities) including bypass secret scenario.
5. Containerization & IaC (Bicep) with two-pass identity assignment.
6. Standalone Python upload client (`apps/upload_client`) with tests covering status mapping.

Outstanding / Recommended Next:
7. Add end-to-end request validation tests (multipart cases, limits, auth failure).
8. Sync central docs (`docs/azure-resources.md`) with env var table + response example + client usage snippet.
9. Add secret hashing command examples (bash, PowerShell).
10. Optional retry wrapper for blob upload (exponential backoff) if error telemetry indicates need.
11. Integrate upload client into candidate service (replace placeholder logic) & add contract tests.
12. Optional Azurite integration tests toggled by env marker.

## Risks & Mitigations
- Multipart parsing memory spikes: ensure chunked read + size counter; reject early.
- Secret misconfiguration: add startup log verifying `INTERNAL_UPLOAD_KEY_SHA256` present.
- Incorrect contextType allow-list causing future adoption friction: document how to append and keep validation table-based.
- Blob path collisions: use UUID fileId prefix; extremely low risk.
- Local vs deployed credential differences: fallback logic clear & documented; explicit warning log if using development connection string instead of managed identity.

## Acceptance Criteria Mapping (Updated)
Goal (generic endpoint) -> Achieved (function implemented, returns metadata).
Hash & metadata integrity -> Implemented (sha256 computed; not yet covered by full request test).
10MB streaming limit -> Enforced in code; boundary test pending.
Minimal logging -> Implemented.
First consumer integration path -> Deferred (no client stub yet).
Demo simplicity (new) -> Achieved via bypass flag, clearly warned.

---
Current completion yields: Core function code + utility tests + Docker + IaC + demo auth bypass. Remaining: broader tests, central documentation sync, integration client, optional reliability enhancements.
