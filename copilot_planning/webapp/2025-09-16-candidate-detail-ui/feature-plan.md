# Feature Plan: Candidate Detail Page with Materials Section

## Problem

Users evaluating decision kits need to inspect individual candidates in depth. Currently, there is no dedicated candidate detail view: candidate information (name, description) and associated materials (documents, links, notes) are not surfaced cohesively. This hinders comparison, context gathering, and auditability of evaluation decisions.

## Goals (acceptance criteria)

- Dedicated route (e.g. `/candidates/:id`) accessible from candidate listings (e.g. decision kit detail page) via navigation.
- Display candidate name (editable future, read-only now) and description.
- Collapsible "Materials" section default expanded if materials exist, collapsed if none.
- Materials section lists candidate materials (documents, links, or placeholders) with filename/title and optional description.
- Graceful empty state when no materials (message + CTA placeholder for future upload/add).
- Loading skeletons while fetching candidate + materials.
- Error state with retry for both candidate core data and materials fetch.
- Responsive layout (single column on mobile, constrained width on desktop).
- Accessible: proper landmarks, headings, buttons with aria-expanded for collapsible section.

## Non-goals

- Uploading or editing candidate materials (future feature; read-only listing now).
- Inline editing of candidate name/description.
- Material preview rendering (PDF/image inline previews) beyond simple link/display.
- Bulk navigation (prev/next candidate) controls.

## Design

### Architecture & Flow

1. User clicks a candidate in Candidates section of Decision Kit detail.
2. Router navigates to `/candidates/:id` (or nested route `/kits/:kitId/candidates/:candidateId` — choose final path based on existing patterns; assume standalone for now with ability to deep-link).
3. CandidateDetailPage component loads:
   - Triggers parallel fetch: candidate core data (name, description) + materials list.
   - Shows skeleton placeholders until resolved.
4. On success: renders header with candidate name & description, then collapsible MaterialsSection.
5. On error: displays error alert with retry button (refetch).

### Components (new)

- `routes/CandidateDetailPage.tsx` — page container, orchestrates data fetching.
- `components/candidates/CandidateHeader.tsx` — name + description display.
- `components/candidates/CollapsibleSection.tsx` — generic accessible collapsible wrapper (can be reused for rubric/candidates/report sections elsewhere).
- `components/candidates/CandidateMaterialsList.tsx` — lists materials or empty state.
- `components/candidates/MaterialItem.tsx` — single material row (icon + name + optional description/link).

### Hooks / Data Layer

- `hooks/useCandidate(id: string)` — fetch candidate (GET /candidates/{id}).
- `hooks/useCandidateMaterials(candidateId: string)` — fetch materials (GET /candidates/{id}/materials) or integrated if API returns embedded materials.
- Caching strategy: simple in-memory state; future enhancement might consolidate with react-query.

### Data Structures (frontend TypeScript)

```ts
export interface Candidate { id: number; name: string; description?: string }
export interface CandidateMaterial { id: number; name: string; type?: string; description?: string; url?: string }
```

If API provides nested shape: `{ candidate: Candidate, materials: CandidateMaterial[] }`, adapt hooks accordingly.

### UX / Styling

- Top spacing consistent with other pages (e.g., Container maxWidth="md").
- Materials section uses disclosure pattern: button with chevron rotates, `aria-controls` referencing content div.
- Empty materials: icon + text "No materials yet" and subtle hint "Upload or add references will appear here".
- Loading: skeleton for header (two lines) and 3 skeleton rows for materials.

### Accessibility

- Page heading `<h1>` = candidate name.
- Collapsible controlled via button element with `aria-expanded` and `aria-controls`.
- List semantics: `<ul>` for materials.

## Impacted code

- New route addition in `apps/webapp/src/App.tsx` (React Router) or router module.
- New: `apps/webapp/src/routes/CandidateDetailPage.tsx`.
- New: `apps/webapp/src/components/candidates/CandidateHeader.tsx`.
- New: `apps/webapp/src/components/candidates/CollapsibleSection.tsx` (generic).
- New: `apps/webapp/src/components/candidates/CandidateMaterialsList.tsx`.
- New: `apps/webapp/src/components/candidates/MaterialItem.tsx`.
- New: `apps/webapp/src/hooks/useCandidate.ts`.
- New: `apps/webapp/src/hooks/useCandidateMaterials.ts`.
- Possibly update: `apps/webapp/src/components/decisionKits/CandidatesView.tsx` to link to candidate detail route.
- API client additions: `apps/webapp/src/api/candidates.ts` for fetch helpers.

## Edge cases and risks

- Candidate has zero materials: ensure collapsed-by-default logic doesn't hide discoverability (decide: show expanded empty state first time — simpler; adjust acceptance criteria accordingly if needed). Current plan: expanded showing empty state.
- Slow materials fetch vs fast candidate fetch: show independent loading indicators; avoid layout jump.
- API returns partial failure (candidate ok, materials fail): show candidate header + error box in materials section with retry limited to materials.
- Very long description or material names: apply CSS line clamp or wrap gracefully.
- Broken material URLs: open in new tab; potential 404 not handled inline (future enhancement).

## Test plan

- Unit: hooks handle success, loading, error states (mock fetch).
- Component: CandidateDetailPage renders skeleton then data.
- Empty materials renders empty state text.
- Error in materials only shows retry without hiding candidate header.
- Collapsible toggles `aria-expanded` and hides/shows content.
- Accessibility: page has role="main" and h1; materials list has list semantics.

## Migration/compat

- Adds new route; no breaking changes to existing pages.
- Optional integration point for decision kit candidate listing linking.

## Rollout

- No feature flag initially; small isolated feature.
- Add minimal README update referencing candidate detail navigation.

## Links

- Related decision kit UI refactor: `copilot_planning/webapp/2025-09-16-decision-kit-ui-refactor/feature-plan.md`
- Backend candidate materials API planning (if exists).
