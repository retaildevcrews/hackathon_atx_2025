# Feature Plan: Rubric CRUD UI with Navigation Drawer

## Problem
The current React UI lacks a dedicated rubric management interface. While rubric components exist for use in decision kits, users need a standalone page to create, view, update, and delete rubrics, each composed of a collection of criteria. Additionally, the app needs improved navigation to access different sections (Home, Decision Kits, Rubrics).

## Goals (acceptance criteria)

- Implement a standalone Rubrics page with full CRUD functionality
- Add a navigation drawer with links to Home, Decision Kits, and Rubrics
- Allow users to create, view, update, and delete rubrics with criteria selection
- Reuse existing rubric components (`RubricList`, `RubricForm`, `RubricDetail`) where possible
- Integrate with existing Rubric API and Criteria API
- Maintain responsive design and accessibility standards

## Non-goals

- Advanced rubric sharing or collaboration features
- Rubric templates or presets
- Bulk operations on rubrics
- Rubric version history

## Design

### Navigation Structure

- Add a persistent navigation drawer (Material-UI `Drawer` component)
- Navigation items: Home (Decision Kits), Decision Kits, Rubrics
- Drawer should be collapsible on mobile devices
- Update `AppLayout` to include the navigation drawer

### Rubric Management Pages

- **Rubrics List Page** (`/rubrics`): Display all rubrics with search/filter capability
- **Rubric Detail Page** (`/rubrics/:id`): View rubric details and associated criteria
- **Add/Edit Rubric Page** (`/rubrics/new`, `/rubrics/:id/edit`): Form for creating/editing rubrics

### Component Reuse Strategy

- Leverage existing `RubricList` component for displaying rubrics
- Enhance `RubricForm` component for standalone create/edit functionality
- Use `RubricDetail` component for detail view
- Reuse `CriteriaList` and criteria selection patterns from decision kit components

### Data Flow

- Extend existing `rubrics.ts` API service with full CRUD operations
- Use React Router for navigation between rubric pages
- Implement proper loading states and error handling
- Cache rubric data appropriately

### UX Examples

```
Navigation Drawer:
├── Home (Dashboard/Decision Kits)
├── Decision Kits
└── Rubrics

Rubrics Page:
- Header with "Add Rubric" button
- Search/filter functionality
- List of rubrics with edit/delete actions
- Click rubric name to view details
```

## Impacted code

- `src/pages/App.tsx`: Add new routes for rubric pages
- `src/pages/layout/AppLayout.tsx`: Add navigation drawer
- `src/pages/rubrics/` (new): Rubric management pages
  - `RubricsListPage.tsx`
  - `RubricDetailPage.tsx`
  - `AddEditRubricPage.tsx`
- `src/components/` (enhance existing):
  - `RubricForm.tsx`: Enhance for standalone use
  - `RubricList.tsx`: Add edit/delete actions
- `src/api/rubrics.ts`: Add missing CRUD operations (create, update, delete)
- `src/components/navigation/` (new): Navigation drawer components

## Edge cases and risks

- Deleting rubrics that are associated with decision kits
- Network errors during CRUD operations
- Concurrent editing of rubrics
- Large numbers of criteria when creating rubrics
- Mobile responsive navigation

## Test plan

- Unit tests for new rubric page components
- Unit tests for enhanced API operations
- Integration tests for rubric CRUD workflows
- Navigation drawer functionality tests
- Responsive design tests for mobile/tablet

## Migration/compat

- Existing rubric components in decision kit context should continue working
- No breaking changes to existing rubric API usage
- Graceful handling of navigation for existing bookmarked URLs

## Rollout

- Feature can be deployed incrementally (navigation first, then rubric pages)
- No feature flags needed - new functionality that doesn't break existing flows
- Monitor API usage patterns for rubric CRUD operations

## Links

- Existing rubric components: `src/components/Rubric*.tsx`
- Material-UI Drawer documentation for navigation patterns
- React Router documentation for nested routing
