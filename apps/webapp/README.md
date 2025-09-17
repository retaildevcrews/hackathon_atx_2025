# Webapp: Criteria & Rubric Manager

This React app allows users to manage document analysis criteria and build rubrics composed of multiple criteria. It integrates with backend APIs for full CRUD operations.

## Features

### Navigation

- Responsive navigation drawer with quick access to Decision Kits and Rubrics
- Mobile-friendly collapsible sidebar

### Criteria Management

- Add, view, edit, and delete criteria
- Form validation and user feedback

### Rubric Management (NEW)

- **Standalone Rubric Pages**: Dedicated interface for managing rubrics
- **Full CRUD Operations**: Create, view, edit, and delete rubrics
- **Criteria Selection**: Build rubrics by selecting from available criteria
- **Search & Filter**: Find rubrics quickly with built-in search
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Delete Protection**: Confirmation dialogs with cascade warnings

### Decision Kit Integration

- Create and manage decision kits with rubric associations
- View decision kit details and associated rubrics

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

## Routes

### Decision Kits

- `/` — Decision kit list (cards) + New Decision Kit button
- `/decision-kits/new` — Create decision kit form
- `/decision-kits/:kitId` — Decision kit detail view

### Rubrics (NEW)

- `/rubrics` — Rubrics list with search and CRUD actions
- `/rubrics/new` — Create rubric form with criteria selection
- `/rubrics/:id` — Rubric detail view showing all criteria
- `/rubrics/:id/edit` — Edit rubric form

## Project Structure
- `src/components/` — UI components for criteria and rubrics
  - `src/components/navigation/` — Navigation drawer component
- `src/pages/` — Route-level components
  - `src/pages/decision-kits/` — Decision kit pages
  - `src/pages/rubrics/` — Rubric management pages (NEW)
  - `src/pages/layout/` — App layout with navigation
- `src/hooks/` — Custom hooks for API integration
- `src/types/` — TypeScript interfaces
- `src/api/` — API service modules with full CRUD operations

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
