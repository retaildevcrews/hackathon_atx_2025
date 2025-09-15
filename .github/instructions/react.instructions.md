---
applyTo: "**/*.tsx,**/*.ts"
---
# GitHub Copilot Agent Development Guidelines

## Project Overview
This is a modern React web application showcasing the GitHub Copilot Agent Onboarding Report. Built with Vite, React, and Tailwind CSS v4+ for optimal development experience and performance.

## Code Quality Standards
- Use modern JavaScript ES6+ features and React functional components with hooks
- Follow React best practices: proper component structure, props validation, and state management
- Use meaningful, descriptive names for variables, functions, and components
- Write self-documenting code with clear comments for complex logic
- Maximum function length: 50 lines, maximum file length: 300 lines
- Prefer composition over inheritance and keep components focused on single responsibilities

## Architecture Principles
- **Component-Based Architecture**: Build reusable, modular components
- **Single Responsibility Principle**: Each component should have one clear purpose
- **Separation of Concerns**: Keep business logic, UI components, and data separate
- **Responsive Design First**: All components must work on mobile, tablet, and desktop
- **Accessibility**: Ensure proper ARIA labels, keyboard navigation, and screen reader support
- **Performance**: Optimize for fast loading, lazy loading where appropriate

## Styling Guidelines
- **Tailwind CSS v4+**: Use utility-first approach with the new @import syntax
- **Dark Mode Support**: All components must support both light and dark themes
- **Mobile-First Design**: Start with mobile layout and progressively enhance
- **Consistent Spacing**: Use Tailwind's spacing scale (4, 8, 16, 24, 32px)
- **Color Scheme**: Primary blue (#3b82f6), Accent purple (#8b5cf6), with proper dark variants
- **Typography**: Use Inter font for UI, JetBrains Mono for code blocks

## React Development Patterns
- Use functional components with hooks (useState, useEffect, useContext)
- Implement proper error boundaries and loading states
- Use React Router for navigation with proper route structure
- Implement context for global state (theme, user preferences)
- Follow React naming conventions: PascalCase for components, camelCase for functions

## File Organization
```
src/
├── components/          # Reusable UI components
├── pages/              # Route-level components
├── contexts/           # React contexts for global state
├── data/               # Static data and content
├── utils/              # Helper functions and utilities
├── hooks/              # Custom React hooks
└── assets/             # Images, icons, and static files
```

## State Management
- Use React Context for global state (theme, user preferences)
- Use useState for local component state
- Implement proper state immutability patterns
- Use useEffect for side effects with proper dependency arrays

## Performance Optimization
- Implement lazy loading for routes and heavy components
- Use React.memo for expensive components that don't change often
- Optimize images and assets for web delivery
- Implement proper code splitting at route level
- Use proper keys in lists to optimize React reconciliation

## Testing Standards
- Write unit tests for utility functions and complex logic
- Test component rendering and user interactions
- Ensure accessibility compliance with automated testing
- Test responsive design across different screen sizes
- Implement integration tests for critical user workflows

## Security Guidelines
- Sanitize all user inputs and content
- Use secure methods for data export (no eval() or dangerous innerHTML)
- Implement proper error handling that doesn't expose sensitive information
- Use HTTPS for all external API calls
- Validate all props and data structures

## Documentation Requirements
- JSDoc comments for all functions and complex components
- README with setup instructions and project overview
- Inline comments for complex business logic
- Component prop documentation with TypeScript-style comments
- Architecture decisions recorded in docs/

## Build and Deployment
- Use Vite for development and production builds
- Implement proper environment variable management
- Configure build optimization for production
- Use modern browser targets for optimal bundle size
- Implement proper CI/CD pipeline checks

## Git Workflow
- Use meaningful commit messages following conventional commits
- Create feature branches for new development
- Implement proper code review process
- Use semantic versioning for releases
- Keep main branch always deployable

## Accessibility Standards
- Use semantic HTML elements appropriately
- Implement proper ARIA labels and descriptions
- Ensure keyboard navigation works for all interactive elements
- Maintain color contrast ratios for WCAG compliance
- Test with screen readers and other assistive technologies

## Error Handling
- Implement proper error boundaries in React
- Use try-catch blocks for async operations
- Provide user-friendly error messages
- Log errors appropriately for debugging
- Implement graceful degradation for failed features

## Content Management
- Keep all content in structured data files for easy maintenance
- Use markdown-friendly format for long-form content
- Implement proper content validation and sanitization
- Support multiple export formats (PDF, Markdown, PNG)
- Maintain content versioning and updates
