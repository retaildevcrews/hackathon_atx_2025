# Candidate Edit UI

## Summary

Enable users to edit an existing candidate's name and description within a decision kit via a dedicated edit page.

## Motivation

Typos or missing contextual details currently require deleting and recreating a candidate, risking loss of materials and historical association ordering. An edit flow improves usability and reduces friction.

## Acceptance criteria

- Edit button appears for each candidate in decision kit detail view
- Clicking navigates to `/decision-kits/:kitId/candidates/:candidateId/edit`
- Form pre-populates existing name + description
- Validation matches create rules; duplicate kit-scoped name shows inline error
- Submitting updates candidate and returns to decision kit detail with refreshed data
- Cancel returns without changes
- Loading and error states clearly communicated

## Scope

In-scope:

- Frontend routed edit page
- Shared form component extraction
- New API util + hook for update

Out of scope:

- Backend update endpoint implementation (assumed or handled separately)
- Materials editing (unchanged)
- Candidate reordering

## Design overview

Reuse create form logic via shared `CandidateForm` supporting create/edit modes. Introduce `updateCandidate` API call. Add edit route and page. Refresh decision kit on success. Show duplicate errors inline.

## Impacted code

- `src/api/candidates.ts` (add update)
- `src/hooks/useUpdateCandidate.ts` (new)
- `src/components/candidates/CandidateForm.tsx` (new)
- `src/pages/candidates/EditCandidatePage.tsx` (new)
- `src/pages/candidates/CreateCandidatePage.tsx` (refactor to use shared form)
- `src/pages/decision-kits/DecisionKitDetailPage.tsx` (add Edit button)
- `src/pages/App.tsx` (route)

## Test plan

- API util tests: success, duplicate error, network failure
- Component test: edit page populates data, submits update, navigates back
- Duplicate name surfaced inline
- No-change submission still navigates back without error

## Risks and mitigations

- Duplicate name collisions -> Reuse existing duplicate handling logic
- Stale kit cache -> Force refetch or optimistic update
- Missing candidate (deleted elsewhere) -> Show not found and navigate back

## Definition of Done

- All acceptance criteria met
- Tests added and passing
- Docs updated (README snippet)
- No regressions in create flow
