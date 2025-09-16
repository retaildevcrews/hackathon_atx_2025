# Webapp: Criteria & Rubric Manager

This React app allows users to manage document analysis criteria and build rubrics composed of multiple criteria. It integrates with backend APIs for full CRUD operations.

## Features
- Add, view, edit, and delete criteria
- Create, view, edit, and delete rubrics (collections of criteria)
- Select criteria when building a rubric
- Form validation and user feedback
- Responsive UI with Material UI

## Usage
1. Install dependencies:
   ```sh
   yarn install
   ```
2. Start the development server:
   ```sh
   yarn dev
   ```
3. Access the app at `http://localhost:5173` (default Vite port)

## API Integration
- Criteria API: `/api/criteria` (GET, POST, PUT, DELETE)
- Rubric API: `/api/rubrics` (GET, POST, PUT, DELETE)

## Project Structure
- `src/components/` — UI components for criteria and rubrics
- `src/hooks/` — Custom hooks for API integration
- `src/types/` — TypeScript interfaces
- `src/pages/App.tsx` — Main app layout

## Decision Kits UI (New)

The refactored Decision Kits interface introduces a routed experience with list and detail pages.

Feature Flag:

- Controlled by `VITE_ENABLE_DECISION_KITS_UI` (default enabled). Set to `false` to fall back to legacy rubric manager.

Routes:

- `/` — Decision kit list (cards with name and description)
- `/decision-kits/:kitId` — Detail view including rubric summary and candidate list

Key Files:

- `src/api/decisionKits.ts` — Fetch functions with in-memory cache
- `src/hooks/useDecisionKits.ts` & `useDecisionKit.ts` — Data hooks with retry
- `src/pages/decision-kits/DecisionKitListPage.tsx`
- `src/pages/decision-kits/DecisionKitDetailPage.tsx`
- `src/pages/layout/AppLayout.tsx`

Testing:

- `src/__tests__/DecisionKits.test.tsx` includes basic list empty state and detail rubric assertions.

Styling & Accessibility:

- Material UI components
- Skeleton loaders during initial fetch
- `twoLineClamp` utility class for description truncation

## Testing
- Add unit and integration tests in `src/__tests__/` (recommended)

## Contributing
- Please see the planning docs in `copilot_planning/webapp/` for feature and implementation plans.
