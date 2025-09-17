# Candidate Edit UI — Feature Plan

## Problem

Users can create candidates within a decision kit and manage their materials, but they cannot edit a candidate's core metadata (name, description). If a name is misspelled or additional descriptive context is needed, the only current workaround is deleting the candidate (losing materials & associations) and recreating it—friction that risks data loss.

## Goals (acceptance criteria)

- User can click an Edit button next to (or within) a candidate entry in a decision kit detail view.
- Edit action navigates to a routed page (`/decision-kits/:kitId/candidates/:candidateId/edit`).
- Form pre-populates existing candidate name + description.
- User can update name (validated same as create: 2–80 chars, allowed charset) and description.
- Submitting updates the candidate and returns the user to the decision kit detail page with refreshed candidate list.
- Validation & duplicate name error (kit-scoped) surfaced inline (same UX pattern as create page).
- Cancel action returns to previous page without persisting changes.
- Loading and error states: skeleton or disabled form while fetching; clear inline error if update fails.

## Non-goals

- Editing candidate materials (already separate flow).
- Bulk editing multiple candidates.
- Reordering candidates (handled elsewhere if needed).
- Changing the decision kit association (candidate remains in same kit).

## Design

- Reuse existing create candidate page component structure; abstract shared logic into a `CandidateForm` component supporting both create and edit modes.
- Add new API method: `updateCandidate(candidateId, payload)`.
  - Payload fields: `{ name: string; description?: string; decisionKitId: string }` (decisionKitId required for duplicate validation scope and potential future reassignment, though not changing now).
- New hook: `useUpdateCandidate` mirroring `useCreateCandidate` (returns mutate fn, loading, error, fieldErrors).
- Route added in `App.tsx`: `/decision-kits/:kitId/candidates/:candidateId/edit` -> `EditCandidatePage` (can be a thin wrapper using `CandidateForm mode="edit"`).
- Duplicate error detection uses same regex / message substring as create ("already exists" or backend detail), mapping to name field error.
- After successful update: navigate back to `/decision-kits/:kitId` and trigger a refetch / invalidation of kit detail query so updated name appears.
- Access pattern: Edit button present in candidate list items within the decision kit detail page (`DecisionKitDetailPage.tsx`). Could be an icon button (MUI) with tooltip.

## Impacted code

- `apps/webapp/src/pages/decision-kits/DecisionKitDetailPage.tsx`: Add Edit button per candidate row.
- `apps/webapp/src/api/candidates.ts`: Add `updateCandidate` function.
- `apps/webapp/src/hooks/useUpdateCandidate.ts` (new) or extend existing hooks index.
- `apps/webapp/src/pages/candidates/CreateCandidatePage.tsx`: Refactor out form portion.
- `apps/webapp/src/pages/candidates/EditCandidatePage.tsx` (new) or reuse same page via mode prop.
- `apps/webapp/src/components/candidates/CandidateForm.tsx` (new shared form component).
- Routing in `apps/webapp/src/main.tsx` or `App.tsx` (whichever defines routes): add edit path.
- Potential minor type adjustments in `src/types/candidates.ts` (e.g., interface for update payload if separate from create).

## Edge cases and risks

- Duplicate candidate name within same kit → ensure backend returns consistent error; frontend must map to name field.
- Candidate deleted in another session before edit load → show not found error and navigate back.
- Slow network causing user to double-submit → disable submit while pending.
- User edits but makes no changes → backend should still respond 200/204; frontend handles gracefully.
- Name normalization rules must match backend (lowercase trim). Avoid client-side premature transformation; only validate.

## Test plan

- Unit tests for `updateCandidate` API util (mock fetch/axios): success, duplicate error, network error.
- Component test: EditCandidatePage loads existing data and submits updated name.
- Validation test: Short name rejected.
- Duplicate name integration: simulate backend 400 and show inline error.
- Navigation test: After success, returns to kit detail and list shows updated name.

## Migration/compat

- No breaking change; new endpoint usage only. Existing create flow untouched except for shared form extraction.
- Ensure any cached kit detail data is invalidated/refetched after update (if using react-query or similar pattern; else manual refetch callback).

## Rollout

- No feature flag needed (simple additive UI feature).
- Optional: Add subtle analytics hook (future) for edit usage.

## Links

- Prior candidate create feature planning (`2025-09-16-candidate-detail-ui`, `2025-09-16-decision-kit-create-delete`).
