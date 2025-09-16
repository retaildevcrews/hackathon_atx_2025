# Decision Kit UI Refactor

## Problem

The current UI is criteria/rubric centric and does not reflect the emerging domain model (candidates, decision kits). Users need a top-level view organized by decisions (kits) with quick access to associated rubric and candidates for evaluation. Without aligning UI structure to domain constructs, navigation becomes fragmented and onboarding slower.


## Goals (acceptance criteria)

### 1. Homepage
  - View all decision kits (lazy loaded)
    - Decision kits are loaded as the user scrolls or paginates
    - Clicking anywhere on a decision kit card opens the Manage/View Decision Kit journey
  - Button for adding a new decision kit

### 2. Add New Decision Kit
  - Simple form with name and description
  - On submit, kit is created and user is redirected to Manage/View Decision Kit

### 3. Manage/View Decision Kit
  - Three main expandable/contractable components:
    - **Rubric**
      - View and CRUD criteria
      - CRUD features for weights for criteria
    - **Candidates**
      - CRUD features for candidates (name, description)
      - CRUD features for candidate documents
      - View candidate assessment
    - **Report**
      - CRUD features for report format
      - View decision kit report
  - Button to delete decision kit
  - Button to “Complete” decision kit (locks kit from editing)
  - Can edit the decision kit name

### Navigation & UX
  - Persistent app header with tabs or sidebar (Decision Kits primary, future Rubrics/Candidates direct access optional)
  - Loading & empty states for list and detail views
  - Error handling surface (toast/snackbar) for failed fetches


## Non-goals

- Advanced creation wizard for decision kits (simple form only for now)
- Bulk import/export of kits, rubrics, or candidates
- Advanced candidate material upload UI (API plan addresses backend; UI deferred)
- Publishing/locking states visual indicators beyond basic “Complete” button


## Design

### Architecture

- Routing (React Router or minimal hash router):
  - `/` (kits list, homepage)
  - `/kits/:id` (kit detail/manage)
  - `/kits/new` (add new kit form)
- State layer: custom hooks `useDecisionKits`, `useDecisionKit(id)` using shared axios client
- Component hierarchy:
  - App
    - AppLayout (header/nav + outlet)
    - DecisionKitListPage (lazy loaded grid/list)
      - DecisionKitCard (MUI Card, clickable)
      - AddDecisionKitButton
    - AddDecisionKitPage (form)
    - DecisionKitDetailPage
      - EditableKitName
      - ExpandableSection: RubricView (CRUD criteria, weights)
      - ExpandableSection: CandidatesView (CRUD candidates, docs, assessment)
      - ExpandableSection: ReportView (CRUD format, view report)
      - DeleteKitButton
      - CompleteKitButton

### Visual

- Material UI Cards with elevation=1, consistent padding
- Grid: MUI Grid or CSS grid with responsive breakpoints (xs=12, sm=6, md=4 for kit list; similar for candidates)
- Typography: h5 for kit name on card, body2 for truncated description (2 line clamp CSS)
- Expandable/contractable sections for Rubric, Candidates, Report
- Skeletons for loading, empty states


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
  rubric: {
    id: number,
    name: string,
    version: number,
    published: boolean,
    criteria: [{ criteria_id: number, weight: number, name?: string }]
  },
  candidates: [{ id: number, name: string, description?: string, documents?: [{ id: number, name: string, url?: string }], assessment?: { ... } }],
  report?: { format: string, content?: string }
}
```

(If API does not yet provide embedded rubric/candidates, UI plan will include a short-term composition fetch pattern.)


### Interactions

- Homepage:
  - Lazy load decision kits as user scrolls/paginates
  - Clicking anywhere on a kit card navigates to Manage/View Decision Kit
  - Add Decision Kit button opens add form
- Add Decision Kit:
  - Simple form, submit creates kit and navigates to detail
- Manage/View Decision Kit:
  - Expand/collapse Rubric, Candidates, Report sections
  - CRUD for criteria, weights, candidates, candidate docs, report format
  - View candidate assessment and report
  - Edit kit name inline
  - Delete kit button
  - Complete kit button (locks editing)
  - Back navigation via header breadcrumb or browser back


### Error & Loading UX

- Skeleton placeholders for cards (3–6) while loading list
- Spinner or skeleton sections for rubric/candidates/report on detail
- Retry button in error placeholder


## Impacted code

- `apps/webapp/src/App.tsx` (add router and layout)
- New: `apps/webapp/src/routes/DecisionKitListPage.tsx` (lazy loaded)
- New: `apps/webapp/src/routes/AddDecisionKitPage.tsx` (form)
- New: `apps/webapp/src/routes/DecisionKitDetailPage.tsx`
- New: `apps/webapp/src/components/decisionKits/DecisionKitCard.tsx`
- New: `apps/webapp/src/components/decisionKits/AddDecisionKitButton.tsx`
- New: `apps/webapp/src/components/decisionKits/EditableKitName.tsx`
- New: `apps/webapp/src/components/decisionKits/RubricInlineView.tsx` (CRUD criteria, weights)
- New: `apps/webapp/src/components/decisionKits/CandidatesView.tsx` (CRUD candidates, docs, assessment)
- New: `apps/webapp/src/components/decisionKits/ReportView.tsx` (CRUD format, view report)
- New: `apps/webapp/src/components/decisionKits/DeleteKitButton.tsx`
- New: `apps/webapp/src/components/decisionKits/CompleteKitButton.tsx`
- New: `apps/webapp/src/hooks/useDecisionKits.ts`
- New: `apps/webapp/src/hooks/useDecisionKit.ts`
- Refactor: existing rubric component (ensure exportable for reuse) or create new simplified viewer
- Shared: `apps/webapp/src/api/apiClient.ts` (if not already created) extend for decision kits endpoints


## Edge cases and risks

- Large number of kits: lazy loading/pagination required
- Missing or delayed candidate/rubric/report data: implement parallel fetch with loading partitions
- API evolution (composition fields not present yet): use fallback multiple calls
- Mobile layout: ensure cards stack (test narrow viewport)
- Locking: ensure “Complete” disables all edit actions


## Test plan

- Homepage:
  - Render kits list with mocked empty response → shows empty state
  - Render kits list with sample data → cards link to detail route
  - Lazy loading works as user scrolls/paginates
  - Add Decision Kit button opens form
- Add Decision Kit:
  - Form validation, successful creation, redirect to detail
- Manage/View Decision Kit:
  - Expand/collapse Rubric, Candidates, Report sections
  - CRUD for criteria, weights, candidates, candidate docs, report format
  - Edit kit name inline
  - Delete kit removes kit and returns to homepage
  - Complete kit disables all edit actions
  - Error boundary displays and retry works for failed detail fetch
  - Accessibility: card clickable area has accessible name (aria-label = kit name)


## Migration/compat

- Introduces routing; existing criteria page can be moved under /legacy or integrated later
- No breaking change to existing components; wrapper layout added


## Rollout

- Ship behind optional env flag `ENABLE_DECISION_KITS_UI` (default true) if quick disable needed
- README section: Using Decision Kits UI

## Links

- Decision Kit API feature: `copilot_planning/api/2025-09-16-decision-kit/feature-plan.md`
- Candidate feature: `copilot_planning/api/2025-09-16-candidate-materials/feature-plan.md`
- Rubric composition refactor: `copilot_planning/api/2025-09-16-rubric-composition-refactor/feature-plan.md`
