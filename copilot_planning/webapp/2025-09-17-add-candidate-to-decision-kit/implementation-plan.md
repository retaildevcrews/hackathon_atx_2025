# Implementation plan — Add Candidates with Materials (Routed Two-Step Flow)

This plan defines discrete, verifiable steps for the agent to implement the feature described in `feature-plan.md`.

## Pre-flight

- [ ] Locate decision kit detail page component and confirm candidates list + navigation pattern
- [ ] Confirm backend endpoints (observed in `apps/criteria_api/app/routes/candidates.py`): `POST /candidates`, `GET /candidates/{id}`, `POST /candidates/{id}/materials`, list + delete endpoints
- [ ] Decide route structure: `/decision-kits/:kitId/candidates/new` and `/candidates/:candidateId/edit`
- [ ] Add/confirm API base config and shared fetch/error utilities
- [ ] Define constants: supported file types/extensions, max file size (10MB), concurrency (1 sequential)
- [ ] Ensure change is additive (no existing route name collisions)

## Implementation

### Data & API layer

- [ ] Create / extend `api/candidates.ts` with:
  - [ ] `postCandidate(data: { name; description?; decisionKitId })`
  - [ ] `getCandidate(id)`
  - [ ] `listCandidateMaterials(candidateId)`
  - [ ] `uploadCandidateMaterial(candidateId, file)` (multipart)
  - [ ] `deleteCandidateMaterial(candidateId, materialId)`
- [ ] (Optional) `listDecisionKitCandidates(kitId)` if not already present
- [ ] Implement abort support for uploads (AbortController per file)

### Hooks

- [ ] `useCreateCandidate()` — create only; returns candidate id
- [ ] `useCandidate(candidateId)` — fetch single candidate (with loading/error)
- [ ] `useCandidateMaterials(candidateId)` — list materials & refresh
- [ ] `useUploadCandidateMaterial(candidateId)` — upload a single file with progress & abort
- [ ] `useDeleteCandidateMaterial(candidateId)` — delete file and refresh
- [ ] `useDecisionKitCandidates(kitId)` — list & refresh for decision kit page

### Components / Routes

- [ ] `AddCandidateButton` — navigates to creation route
- [ ] `routes/CreateCandidatePage.tsx` — candidate form page
- [ ] `routes/EditCandidateMaterialsPage.tsx` — materials management page
- [ ] `components/candidates/CandidateForm.tsx` — reused across create/edit (description only now)
- [ ] `components/candidates/MaterialsUploadZone.tsx`
- [ ] `components/candidates/MaterialsGrid.tsx`
- [ ] `components/candidates/MaterialCard.tsx`
- [ ] (Removed for now) description editor (backend lacks field)

### State & Logic

- [ ] Candidate creation form validation (name required, length constraints)
- [ ] Navigate to edit page after successful create (pass candidate id)
- [ ] Materials draft list (pre-upload) with statuses (`pending|uploading|error|uploaded`)
- [ ] Duplicate filename detection (compare against drafts + existing uploaded list)
- [ ] Sequential uploads (simple for MVP)
- [ ] Retry sets status to uploading; abort support cancels fetch
- [ ] Cleanup object URLs (thumbnails) on unmount
- [ ] Delete material removes from server then refreshes list

### UX & Styling

- [ ] Form page layout (centered container, responsive)
- [ ] Materials page layout (sidebar candidate summary + main grid)
- [ ] Grid styles: square cards, truncated text, icons
- [ ] Error + helper text styling consistent with existing design system
- [ ] Loading indicators (button spinner, per-file uploading overlay)
- [ ] Accessible labels and focus management (focus first invalid field on validation error; focus heading on route change)

### Integration

- [ ] Insert `AddCandidateButton` into decision kit candidate section toolbar/header
- [ ] After creation, upon navigating back (or via toast CTA) ensure decision kit candidate list refetches
- [ ] Success toast/notification (reuse existing pattern or add minimal util)

## Validation

- [ ] Unit tests: API helpers (create candidate, upload, delete) with mocked fetch
- [ ] Hook tests: create candidate flow, upload success/error, delete material
- [ ] Component tests: create page validation; navigation to materials page; materials grid rendering and retry
- [ ] Accessibility: headings, labels, keyboard nav for upload zone

## Samples and documentation

- [ ] Update webapp README with short section "Adding Candidates"
- [ ] Add screenshot or description of materials grid (optional)

## Rollout

- [ ] Add environment variable toggle placeholder (comment) if later needed
- [ ] Confirm no regression in existing candidate listing (manual smoke)
- [ ] Mark feature plan & issue as implemented

## Post-launch (Follow-ups / Stretch)

- [ ] Parallel uploads with concurrency limit
- [ ] Cancel uploads
- [ ] Batch upload endpoint usage if backend adds
- [ ] Material reordering
- [ ] Inline file preview for images/PDF
