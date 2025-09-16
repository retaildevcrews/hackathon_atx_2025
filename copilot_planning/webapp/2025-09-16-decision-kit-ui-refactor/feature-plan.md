# Decision Kit UI Refactor

## Problem

The current UI is criteria/rubric centric and does not reflect the emerging domain model (candidates, decision kits). Users need a top-level view organized by decisions (kits) with quick access to associated rubric and candidates for evaluation. Without aligning UI structure to domain constructs, navigation becomes fragmented and onboarding slower.

## Goals (acceptance criteria)

- Home page shows a grid/list of Decision Kit cards (name + description only per card for clarity; click to drill in).
- Decision Kit detail page displays: name, description, Rubric section, Candidates section.
- Rubric section reuses existing rubric criteria display component (read-only for now) nested within detail.
- Candidates section shows candidate cards (name + description) in responsive grid.
- Navigation: persistent app header with tabs or sidebar (Decision Kits primary, plus future Rubrics / Candidates direct access optional later).
- Loading & empty states for list and detail views.
- Error handling surface (toast/snackbar) for failed fetches.

## Non-goals

- Creating or editing rubrics/candidates inside the Decision Kit detail (future inline actions).
- Implementing Decision Kit creation wizard (can be separate subsequent feature).
- Candidate material upload UI (API plan addresses backend; UI deferred).
- Publishing / locking states visual indicators (future).

## Design

### Architecture

- Introduce routing (React Router or minimal hash router) to support `/` (kits list) and `/kits/:id` (kit detail).
- State layer: custom hooks `useDecisionKits` & `useDecisionKit(id)` using shared axios client.
- Component hierarchy:
  - App
    - AppLayout (header/nav + outlet)
    - DecisionKitListPage
      - DecisionKitCard (MUI Card)
    - DecisionKitDetailPage
      - Section: RubricView (reuses existing or new `RubricInlineView` component)
      - Section: CandidateCardsGrid
        - CandidateCard

### Visual

- Use Material UI Cards with elevation=1, consistent padding.
- Grid: MUI Grid or CSS grid with responsive breakpoints (xs=12, sm=6, md=4 for kit list; similar for candidates).
- Typography: h5 for kit name on card, body2 for truncated description (2 line clamp CSS).

### Data contracts (frontend expectation)

Decision Kit list item:

```ts
{
  id: number,
  name: string,
  description?: string
}
```

Decision Kit detail (expanded):

```ts
{
  id: number,
  name: string,
  description?: string,
  rubric: { id: number, name: string, version: number, published: boolean, criteria: [{criteria_id:number, weight:number, name?:string}] },
  candidates: [{ id:number, name:string, description?:string }]
}
```

(If API does not yet provide embedded rubric/candidates, UI plan will include a short-term composition fetch pattern.)

### Interactions

- Clicking a kit card navigates to detail page.
- Back navigation via header breadcrumb or browser back.
- No inline edit actions (read-only pass).

### Error & Loading UX

- Skeleton placeholders for cards (3–6) while loading list.
- Spinner or skeleton sections for rubric/candidates on detail.
- Retry button in error placeholder.

## Impacted code

- `apps/webapp/src/App.tsx` (add router and layout)
- New: `apps/webapp/src/routes/DecisionKitListPage.tsx`
- New: `apps/webapp/src/routes/DecisionKitDetailPage.tsx`
- New: `apps/webapp/src/components/decisionKits/DecisionKitCard.tsx`
- New: `apps/webapp/src/components/decisionKits/RubricInlineView.tsx`
- New: `apps/webapp/src/components/decisionKits/CandidateCard.tsx`
- New: `apps/webapp/src/hooks/useDecisionKits.ts`
- New: `apps/webapp/src/hooks/useDecisionKit.ts`
- Refactor: existing rubric component (ensure exportable for reuse) or create new simplified viewer.
- Shared: `apps/webapp/src/api/apiClient.ts` (if not already created) extend for decision kits endpoints.

## Edge cases and risks

- Large number of kits may need pagination; MVP loads first page only (document limit).
- Missing or delayed candidate/rubric data: implement parallel fetch with loading partitions.
- API evolution (composition fields not present yet) — use fallback multiple calls.
- Mobile layout: ensure cards stack (test narrow viewport).

## Test plan

- Render kits list with mocked empty response → shows empty state.
- Render kits list with sample data → cards link to detail route.
- Detail page loads rubric + candidates concurrently (mocked) and renders sections.
- Error boundary displays and retry works for failed detail fetch.
- Accessibility: card clickable area has accessible name (aria-label = kit name).

## Migration/compat

- Introduces routing; existing criteria page can be moved under /legacy or integrated later.
- No breaking change to existing components; wrapper layout added.

## Rollout

- Ship behind optional env flag `ENABLE_DECISION_KITS_UI` (default true) if quick disable needed.
- README section: Using Decision Kits UI.

## Links

- Decision Kit API feature: `copilot_planning/api/2025-09-16-decision-kit/feature-plan.md`
- Candidate feature: `copilot_planning/api/2025-09-16-candidate-materials/feature-plan.md`
- Rubric composition refactor: `copilot_planning/api/2025-09-16-rubric-composition-refactor/feature-plan.md`
