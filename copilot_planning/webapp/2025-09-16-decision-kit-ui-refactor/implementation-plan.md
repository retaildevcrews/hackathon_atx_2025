# Implementation Plan — Decision Kit UI Refactor

## Pre-flight

- [ ] Confirm Material UI + existing axios client available
- [ ] Decide router choice (React Router v6) and install if absent
- [ ] Define feature flag `ENABLE_DECISION_KITS_UI` (fallback true if env undefined)
- [ ] Inventory existing rubric display component for reuse or create new inline viewer

## Implementation

- [ ] Add routing wrapper in `App.tsx` (BrowserRouter or HashRouter depending on deploy constraints)
- [ ] Create `AppLayout` (AppBar + Container + Outlet)
- [ ] Decision Kit list page
  - [ ] Hook `useDecisionKits` (GET /decision-kits)
  - [ ] `DecisionKitCard` component (props: id, name, description) with clickable area (onClick -> navigate)
  - [ ] Grid layout + skeleton loaders + empty state
- [ ] Decision Kit detail page
  - [ ] Hook `useDecisionKit(id)` (GET /decision-kits/{id})
  - [ ] Sections: heading (name/description), RubricInlineView, CandidateCardsGrid
  - [ ] `RubricInlineView` fetch rubric if not embedded (fallback pattern)
  - [ ] `CandidateCard` (name, description)
  - [ ] Loading + error placeholders
- [ ] Shared `api/decisionKits.ts` (type definitions + fetch functions)
- [ ] Accessibility pass (aria-label on cards, semantic headings)

## Types

```ts
export interface DecisionKitListItem { id: number; name: string; description?: string }
export interface DecisionKitCandidate { id: number; name: string; description?: string }
export interface RubricCriterionEntry { criteria_id: number; weight: number; name?: string }
export interface RubricSummary { id: number; name: string; version: number; published: boolean; criteria: RubricCriterionEntry[] }
export interface DecisionKitDetail extends DecisionKitListItem { rubric: RubricSummary; candidates: DecisionKitCandidate[] }
```

## State & Caching

- Use simple SWR-like pattern (local state + effect) for hooks; future optimization with react-query if needed
- Basic in-memory cache (Map) for kits by id to avoid refetch when navigating back

## Loading UX

- Skeleton components for card grid (MUI Skeleton inside Card)
- Detail: skeleton title bar + placeholder boxes for sections

## Error Handling

- Central `useApiError` util maps axios errors to user-friendly message
- Retry button triggers refetch in hooks

## Testing (Component-level with Jest + React Testing Library)

- [ ] List page renders skeleton then cards
- [ ] Empty state message when API returns []
- [ ] Card click navigates to detail route (assert URL change)
- [ ] Detail page displays rubric criteria count
- [ ] Error state shows retry and recovers after mock success
- [ ] Accessibility: cards have role=button or are anchor-wrapped

## Styling

- Central theme adjustments if needed (typography for h5 on cards)
- Use line clamp via CSS for description truncation (.twoLineClamp)

## Feature Flag

- Wrap routes in conditional; fallback to legacy criteria view if disabled

## Documentation

- README UI section update (screenshots placeholders, route overview)
- Developer note describing data fetch composition if API lacks embedded rubric/candidates initially

## Rollout Steps

1. Implement hooks + API module
2. Add routing + layout
3. Build list + card components
4. Build detail page + sections
5. Integrate rubric viewer reuse
6. Add loading/error states
7. Add tests
8. Update README

## Manual Smoke Checklist

- Home shows kit cards
- Navigating to kit detail shows rubric + candidates
- Browser back returns to preserved list scroll
- Network error surfaces toast
- Feature flag off hides new UI

## Risks & Mitigations

- Missing embed fields → sequential fetch; mitigate with parallel chained calls
- Large candidate arrays cause tall detail page → consider scroll anchor links (future)

## Completion Definition

- All acceptance criteria satisfied
- CI tests (if configured) pass
- Lint passes (no unused vars) and build succeeds
