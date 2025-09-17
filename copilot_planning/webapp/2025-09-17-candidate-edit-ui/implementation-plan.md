# Implementation Plan — Candidate Edit UI

## Pre-flight

- [ ] Confirm backend supports candidate update endpoint (if missing, plan separate backend task or reuse existing update service when added)
- [ ] Decide whether to reuse Create page component or introduce shared `CandidateForm`
- [ ] Identify all routes to adjust (add edit route)

## Implementation

- [ ] Create `CandidateForm` component extracting form logic (fields, validation display, submit button, error mapping)
- [ ] Add API method `updateCandidate(id, payload)` in `src/api/candidates.ts`
- [ ] Add hook `useUpdateCandidate` mirroring `useCreateCandidate`
- [ ] Add route `/decision-kits/:kitId/candidates/:candidateId/edit` in `App.tsx` (lazy loaded)
- [ ] Create `EditCandidatePage` wrapper using `CandidateForm` in edit mode: loads candidate, populates form, handles submit
- [ ] Insert Edit button/IconButton in candidate row within `DecisionKitDetailPage.tsx` linking to new route (preserve kitId context)
- [ ] Ensure navigation after successful update invalidates/refetches decision kit detail data
- [ ] Disable submit while request in-flight to avoid duplicate submissions
- [ ] Add Cancel button -> navigates back to kit detail page without changes

## Validation

- [ ] Add unit test for `updateCandidate` API util (success + duplicate + network error)
- [ ] Component test: Edit page loads existing data and submits change
- [ ] Duplicate name test: simulate backend 400 maps to name field error
- [ ] No-change submit still returns success path

## Samples and documentation

- [ ] Update README (webapp section) describing edit flow
- [ ] Add brief usage note in planning docs referencing shared form component

## Rollout

- [ ] Confirm build passes and tree-shaking unaffected
- [ ] Manually test navigation create -> edit -> materials path
- [ ] Verify bundle size impact minimal (shared form reduces duplication)
