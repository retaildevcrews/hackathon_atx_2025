# GitHub Issue: Candidate Detail Page with Materials Section

## Summary

Add a dedicated Candidate Detail page that displays candidate name, description, and a collapsible Materials section listing associated materials (documents/links). Read-only for now.

## Motivation

Evaluators need a focused view of each candidate and its supporting materials to make informed, auditable assessments. Currently, candidate context is fragmented or absent, slowing evaluation and increasing risk of overlooking critical artifacts.

## Acceptance Criteria

- [ ] Route exists: `/candidates/:id` (or nested variant) accessible via candidate list links
- [ ] Page shows candidate name as heading and description below
- [ ] Materials section present with toggle control (button with aria-expanded)
- [ ] Materials list renders each material name and optional description/link
- [ ] Empty materials shows descriptive empty state when none
- [ ] Loading skeletons for header and materials
- [ ] Error state for candidate fetch (full-page) with retry
- [ ] Error state for materials fetch (section-only) with retry
- [ ] Responsive layout (mobile single column)
- [ ] Basic accessibility: proper headings, list semantics, toggle ARIA
- [ ] Tests cover success, empty, error, and toggle behavior

## Scope

Included:

- New route + page component
- Hooks for fetching candidate and materials
- Collapsible materials section
- Linking from existing candidate list (if present)

## Out of Scope

- Editing candidate or materials
- Adding/uploading materials
- Previewing content inline
- Pagination or filtering materials

## Design Overview

- React Router addition for candidate detail route
- `CandidateDetailPage` orchestrates two parallel fetches (candidate + materials)
- `CollapsibleSection` generic disclosure pattern reused for future sections
- Materials list simple vertical list with icons

## Impacted Code

- `src/App.tsx` (add route)
- New components under `src/components/candidates/`
- New hooks `useCandidate`, `useCandidateMaterials`
- New API module `src/api/candidates.ts`
- Update candidate list UI (linking) if exists

## Test Plan

- Render page (success): shows header + materials
- Empty materials: shows empty state
- Candidate fetch error: shows full-page retry
- Materials fetch error: section error + retry recovers
- Toggle hides/shows materials content (aria-expanded changes)
- Snapshot or query-based checks for skeleton on initial load

## Risks and Mitigations

- Partial failure (materials only) → isolate error UI in section
- API latency → skeleton placeholders
- Route path divergence later (nested under kits) → design route util to compose path centrally

## Definition of Done

- All acceptance criteria satisfied
- Code merged with passing tests/lint/build
- README or docs updated referencing candidate detail navigation
