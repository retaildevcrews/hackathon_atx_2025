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

## Testing
- Add unit and integration tests in `src/__tests__/` (recommended)

## Contributing
- Please see the planning docs in `copilot_planning/webapp/` for feature and implementation plans.
