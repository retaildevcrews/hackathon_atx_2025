# Feature Plan: Add Candidates with Materials to Decision Kit (Routed Creation Flow)

## Problem

Decision kit owners need to add candidates (entities being evaluated) directly within the decision kit UI. Today (assumed current state), you can view existing candidates (or none), but cannot create a new candidate with its contextual supporting materials in one cohesive, guided flow. Supporting documents (resumes, specs, images, briefs) are critical for evaluators to make informed rubric-based scoring decisions. Lack of candidate creation + material attachment leads to:

- Fragmented workflows (manual out-of-band sharing)
- Missing context during evaluation sessions
- Higher risk of inconsistent or biased scoring due to incomplete info

## Goals (acceptance criteria)

- From a Decision Kit detail page, user can click "Add Candidate" which navigates to routed page `/decision-kits/:kitId/candidates/new`.
- Routed page (Step 1) presents form to create candidate: name (required, max 120), description (optional, max 2000), and optional inclusion in decision kit (kitId pre-populated from route).
- User submits form → POST `/candidates` (payload includes `decisionKitId` per backend) creating candidate; on success redirect to `/candidates/:candidateId/edit` (Step 2) OR show inline second panel (choose two-route approach for clarity).
- Materials can only be added after candidate exists (candidate id known); Step 2 page shows Materials section with upload grid.
- User can upload 0..N materials (documents or images). Supported types initial: PDF, DOCX, PNG, JPG, TXT (configurable constant). (Backend `upload_material` currently stores only file; no description field — description support is deferred or requires backend extension; note in Non-goals.)
- Materials displayed in a responsive square card grid (min 140px side, flex-wrap, consistent aspect) with:
  - File type icon or image thumbnail (if image)
  - Truncated filename (tooltip on hover)
  - Upload status badge (Uploading, Error retry, Done)
  - Remove (X) button (before uploaded; after upload triggers DELETE endpoint)
- Drag & drop + click-to-select upload supported.
- Validation errors surfaced inline (unsupported type, > size limit e.g., 10MB, duplicate filename in current session).
- Candidate creation errors surfaced inline at top of form with retry.
- After materials uploads, grid updates in-place; page offers navigation back to decision kit detail.
- Accessible: routed pages have proper headings, landmarks; materials grid uses list semantics.
- Loading states: skeleton or spinner for candidate load on edit page; per-file progress indicators.

## Non-goals

- Modal-based flow (replaced by routed multi-step flow).
- Material description editing (backend currently lacks description field on upload endpoint; adding would be a backend extension — out of scope for this iteration).
- Reordering materials post-upload.
- Inline preview or download inside page beyond basic link/thumbnail.
- Bulk upload progress consolidation UI beyond simple per-file badge.
- Server-side virus scanning or content analysis.

## Design

### Interaction Flow

1. User clicks "Add Candidate" on Decision Kit detail page.
2. App routes to `/decision-kits/:kitId/candidates/new`.
3. User enters name & description and submits.
4. Frontend calls `POST /candidates` with `{ name, description, decisionKitId: <kitId> }`.
5. On success, navigate to `/candidates/:candidateId/edit`.
6. Edit page loads candidate via `GET /candidates/:candidateId` and materials via `GET /candidates/:candidateId/materials` (initially empty list).
7. User uploads materials (each triggers `POST /candidates/:candidateId/materials` multipart with `file`).
8. Each successful upload appends to grid; errors mark card with retry.
9. User may delete a material via `DELETE /candidates/:candidateId/materials/:materialId` before leaving.
10. User clicks "Back to Decision Kit" returning to kit detail (which refetches candidate list showing new candidate).

### API Alignment (Observed Backend: `apps/criteria_api/app/routes/candidates.py`)

- `POST /candidates` expects `CandidateCreate` (includes optional `decisionKitId`). Returns `Candidate`.
- `GET /candidates/{candidate_id}` returns `Candidate`.
- `POST /candidates/{candidate_id}/materials` accepts `file` (UploadFile). Response: `CandidateMaterial` (no description field present; grid will not show editable description now).
- `GET /candidates/{candidate_id}/materials` returns `CandidateMaterialList`.
- `DELETE /candidates/{candidate_id}/materials/{material_id}` removes a material.
- `DELETE /candidates/{candidate_id}` deletes candidate and materials.

Implication: Material description feature deferred unless backend expanded. UI will omit description editor and acceptance criteria updated accordingly.

If backend supports batch upload endpoint (e.g., `/candidates/{id}/materials/batch`), can optimize; default individual uploads.

### Data Structures (TypeScript)

```ts
export interface NewCandidateInput { name: string; description?: string; decisionKitId: string }
export interface Candidate { id: string; name: string; description?: string; decisionKitId?: string }
export interface CandidateMaterialDraft { id: string; file: File; status: 'pending'|'uploading'|'error'|'uploaded'; errorMessage?: string }
export interface CandidateMaterial { id: string; name: string; type?: string; url?: string }
```

### Components (New / Updated)

- `components/candidates/AddCandidateButton.tsx` — navigates to new candidate route.
- `routes/CreateCandidatePage.tsx` — Step 1 form page.
- `routes/EditCandidateMaterialsPage.tsx` — Step 2 materials management page.
- `components/candidates/CandidateForm.tsx` — name + description fields.
- `components/candidates/MaterialsUploadZone.tsx` — drag/drop & input[type=file].
- `components/candidates/MaterialsGrid.tsx` — grid layout wrapper.
- `components/candidates/MaterialCard.tsx` — square card representing a draft or uploaded material (no description editor now).

### Hooks / State

- `hooks/useCreateCandidate()` — creates candidate only (no materials in same operation).
- `hooks/useCandidate(candidateId)` — fetch single candidate.
- `hooks/useCandidateMaterials(candidateId)` — fetch list of materials.
- `hooks/useUploadCandidateMaterial(candidateId)` — upload single file.
- `hooks/useDeleteCandidateMaterial(candidateId)` — delete material.
- `hooks/useDecisionKitCandidates(kitId)` — list candidates for a kit (refresh after creation or return).

### Styling & Layout

- CreateCandidatePage: centered form, max width constraint.
- EditCandidateMaterialsPage: two-column on wide screens (candidate summary sidebar + materials grid main) collapsing to single column on mobile.
- Grid: CSS grid `auto-fill, minmax(140px, 1fr)` with square cards via `aspect-ratio: 1 / 1`.
- File type icon mapping by extension; images show thumbnail via `URL.createObjectURL` (revoked after upload complete or component unmount).
- Cards status badges (Uploading..., Error (retry), Remove (pre-upload), Delete (post-upload), Done checkmark).

### Accessibility

- Each routed page has `<h1>` ("New Candidate" / "Candidate Materials").
- Grid exposed as list role; each card `role="listitem"`.
- File input accessible label and keyboard-triggerable drop zone.
- Error messages associated with fields via `aria-describedby`.
- Focus moved to first heading on route change.

### Error Handling Strategy

Candidate creation: show inline error summary; user can fix and retry. Materials: each file independent; failure marks card with retry. Deletions optimistic with fallback on failure (restore card). No rollback of candidate on material failures.

### Logging / Analytics (optional)

- Console avoided; use existing logging/telemetry patterns if present (else TODO placeholder for future instrumentation).

## Impacted code

- Add new components under `apps/webapp/src/components/candidates/` (see list above).
- Add new hooks under `apps/webapp/src/hooks/` (`useCreateCandidate.ts`, possibly `useDecisionKitCandidates.ts`).
- Possibly update existing Decision Kit detail page component (e.g., `apps/webapp/src/pages/DecisionKitDetailPage.tsx` or similar) to include `AddCandidateButton` (exact path to confirm in repo — assumption required).
- New API helper: `apps/webapp/src/api/candidates.ts` with `postCandidate`, `postCandidateMaterial`, maybe `getDecisionKitCandidates` (if not existing).
- Update candidate list UI to optimistically insert new candidate (component path TBD once inspected).

## Edge cases and risks

- Large files near size limit -> need immediate client-side rejection with message.
- Duplicate filenames — append numeric suffix or reject; MVP: reject with inline error.
- Slow uploads — ensure spinner doesn't block entire modal; allow cancel (stretch, not in MVP).
- User closes modal mid-upload — abort fetch requests (use AbortController) to avoid orphan uploads.
- Network failure mid-multiple uploads — partial success state needs clarity; keep successful ones.
- Accessibility regressions if focus not restored to Add button after close.
- Memory leak from unreleased object URLs — ensure cleanup.

## Test plan

Unit / Component tests:

- Form validation: required name, length constraints.
- Upload zone: accepts valid file types; rejects invalid.
- MaterialsGrid renders correct number of cards and status indicators.
- Error state for duplicate filename.
- Successful candidate creation navigates to materials page.
- Retry upload updates status from error to uploaded.

Integration (if feasible):

- Mock API create then navigate then uploads sequence.
- Candidate list on decision kit page reflects new candidate after returning.

Accessibility tests:

- Route change sets focus appropriately.
- ARIA labels present for buttons and file input.

## Migration/compat

- Pure additive; no breaking changes to existing candidate display.
- Backend must already support candidate creation and material upload endpoints; if not, align with backend plan (see related API planning docs if present).

## Rollout

- No feature flag (small isolated feature). Could add `ENABLE_CANDIDATE_CREATION` env guard if needed.
- Add brief docs section in webapp README for candidate creation UX.
- Monitor error rates in network tab manually (no telemetry yet).

## Links

- Related prior plan: `2025-09-16-candidate-detail-ui` for viewing candidate + materials.
- API planning: `copilot_planning/api/2025-09-16-candidate-materials/feature-plan.md` (assumed existing for backend).
