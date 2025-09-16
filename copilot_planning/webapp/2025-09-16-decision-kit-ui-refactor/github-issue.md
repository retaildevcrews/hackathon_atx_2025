# GitHub Issue: Decision Kit UI Refactor

## Title

Refactor UI to surface Decision Kits (cards) and detail view (rubric + candidates)

## Summary

Restructure the web application so the home page lists Decision Kits as cards. Each card links to a detail view showing rubric info and candidate cards, aligning UI with the new domain model.

## Motivation

Domain alignment improves discoverability and streamlines evaluation flows. Current UI misses the organizing concept of a decision kit and forces users to piece together rubric and candidate context manually.

## Acceptance criteria

- Home route shows list (or empty state) of decision kit cards (name + description)
- Clicking a card navigates to detail view
- Detail view includes kit name, description, rubric section (read-only), candidates grid
- Loading skeletons show during fetch
- Errors surface with retry option
- Accessible card interactions (keyboard + aria labels)

## Scope

Included:

- Routing introduction
- Decision kit list + detail components
- Hooks for fetching kits and kit detail
- Reuse of rubric display within detail page

Excluded:

- Creation/edit flows for kits, candidates, or rubrics
- Candidate materials display
- Pagination (first page only)

## Out of scope

- Inline editing
- Filtering/search UI (future)
- Mobile-specific optimizations beyond responsive grid

## Design overview

- React Router for `/` and `/kits/:id`
- Card grid (MUI) for list; detail uses stacked sections
- Hooks `useDecisionKits`, `useDecisionKit`
- Shared axios client for API calls

## Impacted code

- `src/App.tsx`
- `src/layout/AppLayout.tsx` (new)
- `src/routes/DecisionKitListPage.tsx`
- `src/routes/DecisionKitDetailPage.tsx`
- `src/components/decisionKits/DecisionKitCard.tsx`
- `src/components/decisionKits/RubricInlineView.tsx`
- `src/components/decisionKits/CandidateCard.tsx`
- `src/hooks/useDecisionKits.ts`
- `src/hooks/useDecisionKit.ts`
- `src/api/decisionKits.ts`

## Test plan

- List renders cards
- Empty state renders when API returns []
- Navigation to detail triggers detail fetch
- Rubric section renders criteria count
- Candidate cards render names
- Error state with retry recovers

## Risks and mitigations

- API composition gaps (fetch rubric/candidates separately) → implement fallback
- Performance with many kits → future pagination

## Definition of Done

- All acceptance criteria satisfied
- README updated with new navigation description
- Tests pass & lint clean
