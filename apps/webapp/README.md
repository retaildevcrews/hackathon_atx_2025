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

- Controlled by `VITE_ENABLE_DECISION_KITS_UI` (if implemented) default enabled.

Routes:

- `/` — Decision kit list (cards) + New Decision Kit button
- `/decision-kits/new` — Create form
- `/decision-kits/:kitId` — Detail view

Key Files:

- `src/api/decisionKits.ts`
- `src/hooks/useDecisionKits.ts`, `src/hooks/useDecisionKit.ts`
- `src/pages/decision-kits/DecisionKitListPage.tsx`
- `src/pages/decision-kits/AddDecisionKitPage.tsx`
- `src/pages/decision-kits/DecisionKitDetailPage.tsx`

Testing:

- `src/__tests__/DecisionKitCreateDelete.test.tsx` basic form tests

Styling & Accessibility:

- Material UI components, skeleton loaders, accessible dialog & buttons

## Decision Kits: Create & Delete

The UI supports creating new decision kits and deleting existing ones (with cascade removal of associated rubric links, weights, candidates, materials, and assessments).

Creating a kit:

- Navigate to the Decision Kits list.
- Click the "New Decision Kit" button (or navigate directly to `/decision-kits/new`).
- Provide a required name and optional description.
- On success you are redirected to the kit detail view.

Deleting a kit:

- From the kit detail page click the Delete button.
- Confirm cascade deletion in the dialog (checkbox required) and click Delete.
- On success you are returned to the list with a confirmation toast.

Edge Cases:

- If the kit was already removed (404), the UI treats the deletion as successful and shows a warning toast.
- Locked kits (409) display an error and remain intact.

## Testing
- Add unit and integration tests in `src/__tests__/` (recommended)

## Contributing
- Please see the planning docs in `copilot_planning/webapp/` for feature and implementation plans.
