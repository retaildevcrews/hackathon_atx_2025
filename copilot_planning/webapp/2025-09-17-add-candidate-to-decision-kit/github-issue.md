# Add ability to create candidate with materials (webapp, routed two-step)

## Summary

Enable users to add a new candidate (name, description) to a decision kit via a dedicated routed page, then manage its uploaded materials (documents/images) on a follow-up materials page.

## Motivation

Evaluators need centralized contextual artifacts (resumes, design briefs, images) to make rubric-based assessments. Currently, adding candidates without their documents leads to fragmented context, manual sharing, and potential inconsistency in scoring.

## Acceptance criteria

- "Add Candidate" button on Decision Kit detail page navigates to `/decision-kits/:kitId/candidates/new`.
- Create Candidate page: form with name (required, max 120), description (optional, max 2000), submit button disabled until valid.
- Successful create (POST /candidates) including `decisionKitId` redirects to `/candidates/:candidateId/edit` (materials page).
- Materials page loads candidate + existing materials (initially none) and presents upload zone (drag & drop + click) for PDF, DOCX, PNG, JPG, TXT (10MB/file limit).
- Materials displayed as square cards grid with file icon or thumbnail, filename truncation, status (uploading, error w/ retry, done), delete control for uploaded files.
- Duplicate filenames (case-insensitive) rejected client-side with inline message.
- Each file upload is independent; failure shows retry action without blocking others.
- Deleting a material calls DELETE endpoint and removes card (optimistic, revert on failure).
- Navigation control to return to original decision kit detail triggers candidate list refresh.
- Accessible routed pages: headings, labels, focus set to page title on navigation, keyboard operable uploads.
- Tests cover create flow, validation errors, upload success + error retry, delete, duplicate filename rejection.
- (Note) Material descriptions not included (backend endpoint lacks description parameter).

## Scope

In-scope:

- Routed candidate creation + materials management pages
- API integration for creation, listing materials, uploading, deleting
- Client-side validation & duplicate filename checks
- Grid layout + icons/thumbnail, sequential uploads

Out of scope:

- Material descriptions (backend not yet supporting)
- Batch upload endpoint / parallel concurrency tuning
- Inline file preview
- Candidate edit after initial creation (beyond materials management)
- Internationalization

## Design overview

Flow: user clicks Add Candidate → routed create page → submit -> backend create → redirect to materials page → upload files individually (sequential) → manage (retry/delete) → navigate back to decision kit detail (list refreshes). Grid uses CSS grid with aspect-ratio for square cards.

## Impacted code

- New routes & components under `src/routes` and `src/components/candidates/*`
- Hooks: `useCreateCandidate`, `useCandidate`, `useCandidateMaterials`, `useUploadCandidateMaterial`, `useDeleteCandidateMaterial`, `useDecisionKitCandidates`
- API utilities `src/api/candidates.ts`
- Decision kit detail page updated (Add button + post-return refresh)

## Test plan

Unit:

- API utilities (mock fetch)
- Hooks success/error paths, retry, delete

Component:

- Create page validation errors (empty name, too long)
- Materials page upload rejection (type, size, duplicate)
- Grid render with multiple files
- Error card retry updates status
- Delete removes card

Integration (if env available):

- Create → redirect → upload sequence

Accessibility:

- Route focus management, keyboard navigation, ARIA labels

## Risks and mitigations

- Large file slow: indicate uploading status → spinner overlay
- Partial failures: keep successful uploads; mark failed + allow retry
- Duplicate file names: block early to avoid server-side conflict
- User navigates away mid-upload: abort requests using AbortController

## Definition of Done

- All acceptance criteria satisfied
- Tests passing locally (unit + component)
- Lint and build succeed
- Documentation updated (webapp README section)
- Feature & implementation plans updated (checked off) or referenced in issue closure note
