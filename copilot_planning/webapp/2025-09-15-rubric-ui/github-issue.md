# GitHub Issue: Rubric CRUD UI with Navigation Drawer

## Summary
Implement a comprehensive rubric management system with full CRUD functionality and improved navigation. Add a navigation drawer to provide easy access to Home, Decision Kits, and Rubrics sections. Create standalone rubric pages that allow users to create, view, update, and delete rubrics with criteria selection. Reuse existing rubric components where possible and integrate with the existing Rubric and Criteria APIs.

## Acceptance Criteria

### Navigation

- [ ] Add navigation drawer with links to Home, Decision Kits, and Rubrics
- [ ] Navigation drawer is responsive and collapsible on mobile devices
- [ ] Current page is properly highlighted in navigation
- [ ] Navigation works seamlessly with React Router

### Rubric List Management

- [ ] User can view a list of all rubrics at `/rubrics`
- [ ] Rubric list includes search/filter functionality
- [ ] Each rubric shows name, description, and action buttons (edit/delete)
- [ ] "Create Rubric" button navigates to creation form
- [ ] Loading and empty states are properly displayed

### Rubric Creation and Editing

- [ ] User can create a new rubric at `/rubrics/new`
- [ ] User can edit an existing rubric at `/rubrics/:id/edit`
- [ ] Form includes name, description, and criteria selection
- [ ] Criteria are fetched from the Criteria API for selection
- [ ] Form validation prevents submission of invalid data
- [ ] Success/error messages are displayed after operations

### Rubric Detail View

- [ ] User can view rubric details at `/rubrics/:id`
- [ ] Detail view shows rubric name, description, and associated criteria
- [ ] Edit and delete buttons are available with proper permissions
- [ ] Breadcrumb navigation is implemented

### Rubric Deletion

- [ ] User can delete a rubric with confirmation dialog
- [ ] Deletion handles potential conflicts with decision kits gracefully
- [ ] User is redirected to rubrics list after successful deletion

### API Integration

- [ ] All CRUD operations integrate with Rubric API endpoints
- [ ] Error handling for network failures and API errors
- [ ] Proper loading states during API calls
- [ ] Cache invalidation after create/update/delete operations

### Component Reuse

- [ ] Existing `RubricList`, `RubricForm`, and `RubricDetail` components are enhanced and reused
- [ ] Components maintain consistency with existing design patterns
- [ ] No breaking changes to existing decision kit functionality

### Responsive Design and Accessibility

- [ ] All pages work properly on mobile, tablet, and desktop
- [ ] Navigation drawer adapts to screen size
- [ ] Keyboard navigation works throughout the interface
- [ ] Screen reader compatibility is maintained
- [ ] Color contrast and font sizes meet accessibility standards

### Testing

- [ ] Unit tests cover new components and API operations
- [ ] Integration tests validate CRUD workflows end-to-end
- [ ] Responsive design is tested across viewports
- [ ] Accessibility compliance is validated

## Technical Requirements

- Use Material-UI components for consistent design
- Follow React best practices and TypeScript patterns
- Maintain existing code quality and linting standards
- Ensure backward compatibility with decision kit features
- Implement proper error boundaries and loading states

## Additional Notes

- Reuse existing rubric components from decision kit implementation
- Consider performance implications with large numbers of rubrics/criteria
- Ensure mobile-first responsive design approach
- Plan for future enhancements like rubric templates and sharing

## Definition of Done

- [ ] All acceptance criteria are met and tested
- [ ] Code review completed and approved
- [ ] Documentation updated (README, component docs)
- [ ] No regressions in existing functionality
- [ ] Performance benchmarks meet standards
- [ ] Accessibility audit passes
- [ ] Mobile testing completed across devices
