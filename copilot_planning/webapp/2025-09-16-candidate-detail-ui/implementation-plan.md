# Implementation Plan — Candidate Detail Page with Materials Section

## Pre-flight

- [ ] Confirm router already integrated (if not, ensure React Router v6 installed)
- [ ] Validate existing API client pattern (axios) and add candidates module
- [ ] Decide final route pattern (`/candidates/:id` vs nested) — assume standalone for initial PR
- [ ] Confirm design alignment with Decision Kit UI refactor for consistency (layout, theming)

## Implementation

- [ ] Add route entry in `App.tsx`
- [ ] Create `api/candidates.ts` with `getCandidate(id)` and `getCandidateMaterials(id)`
- [ ] Create TypeScript types (Candidate, CandidateMaterial)
- [ ] Hook: `useCandidate(id)` (loading, error, data, retry)
- [ ] Hook: `useCandidateMaterials(id)` (separate loading/error states)
- [ ] Component: `CandidateHeader` (renders skeleton while loading)
- [ ] Component: generic `CollapsibleSection` (props: id, title, defaultExpanded, loading, error, onRetry)
- [ ] Component: `CandidateMaterialsList` (empty state, loading skeleton rows, error region)
- [ ] Component: `MaterialItem` (icon by type, link if url)
- [ ] Page: `CandidateDetailPage` orchestrates hooks, passes states to children
- [ ] Update existing candidate list (if present) to navigate to detail page (e.g., `navigate(/candidates/${id})`)
- [ ] Basic responsive styling (Container maxWidth="md")
- [ ] Add accessibility attributes (aria-expanded, aria-controls, role=list)

## Validation

- [ ] Unit test hooks: success, error, retry logic
- [ ] Component test: header skeleton then data
- [ ] Component test: materials empty state
- [ ] Component test: materials error + retry recovers
- [ ] Collapsible toggles visibility + aria-expanded change
- [ ] Snapshot / DOM queries for skeleton nodes existence pre-load

## Samples and documentation

- [ ] README: Add section "Candidate Detail Page" with route and description
- [ ] (Optional) Add screenshot placeholders

## Rollout

- [ ] Merge behind stable route (no flag needed)
- [ ] Verify navigation from Decision Kit candidate list works
- [ ] Confirm build & tests pass in CI

## Post-merge Follow-ups (Not in Scope)

- [ ] Add editing for candidate info
- [ ] Add material upload / attach workflows
- [ ] Inline previews for common file types
- [ ] Breadcrumb nav (e.g., back to kit) if nested route adopted later
