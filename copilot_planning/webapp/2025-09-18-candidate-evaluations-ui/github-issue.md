# Feature: Candidate Latest Evaluation UI

## Summary

Add UI elements on the decision kit detail page to surface a candidate's latest evaluation score and provide navigation to a page showing the full latest evaluation details for that candidate.

## Motivation

Currently after running an evaluation there is no visibility into results unless inspecting backend data. Users need immediate feedback (latest score) and a way to inspect evaluation metadata to inform subsequent decisions without redundant re-runs.

## Acceptance criteria

- Candidate tile shows latest evaluation overall score (badge/caption) if ≥1 evaluation exists.
- Candidate tile displays a "View Eval" (or similar) button only when evaluations exist.
- Clicking the button navigates to a dedicated latest evaluation page.
- Latest evaluation page displays: overall score, rubric name, created timestamp (human readable), and candidate-specific breakdown (score + rank if available).
- If no evaluations exist (race condition) page gracefully shows empty state + back link.
- Errors in fetching evaluations show retry affordance.
- Performance: initial decision kit render not blocked by evaluation fetch (async after paint).

## Scope (in)

- API helpers for fetching evaluation summaries & detail.
- Hook for candidate evaluations (caching latest summary).
- UI modifications to candidate tile.
- New route + page for latest evaluation detail.
- Basic loading / error / empty states.

## Out of scope

- Historical evaluation list navigation.
- Deletion or editing of evaluations.
- Trend/graph visualizations.
- Batch multi-candidate comparison UI.

## Design overview

- Lazy per-candidate fetch to `/candidates/{id}/evaluations` to obtain summaries; pick newest by `created_at`.
- On navigation to latest page, fetch full evaluation by id (use `/candidates/evaluations/{evaluation_id}`).
- Cache summaries & detail in simple Maps to avoid refetch on back navigation.
- Extend Evaluate button logic to invalidate that candidate's cache after starting a new evaluation (optimistic refresh attempt after short delay could be future improvement, not required now).

## Impacted code

- `DecisionKitDetailPage.tsx` (introduce `CandidateTile` subcomponent or refactor list loop)
- New: `api/evaluations.ts`, `types/evaluations.ts`, `hooks/useCandidateEvaluations.ts`
- New page: `pages/candidates/CandidateLatestEvaluationPage.tsx`
- Routing updates in `App.tsx`
- Optional presentational component `components/evaluations/CandidateEvaluationDetail.tsx`

## Test plan

- Unit tests for API helpers (success + error paths).
- Hook test ensuring latest chosen by timestamp.
- Component test candidate tile: no badge before fetch, badge after fetch, absent when zero results.
- Page test rendering evaluation detail.
- Error simulation: show retry and recover.

## Risks & mitigations

- N+1 requests for many candidates: Acceptable for now; monitor. Could batch later.
- Inconsistent timestamp parsing: Use Date parsing + ISO strings; guard for invalid date.
- Missing per-candidate breakdown: fallback to overall score only.

## Definition of Done

- All acceptance criteria satisfied.
- Tests passing (new tests added for API + hook + UI cases).
- No TypeScript errors; lint clean for touched files.
- Documentation (webapp README) updated briefly.
- Manual QA: evaluate candidate → score appears; can view evaluation detail.

## Additional notes

- Future enhancement: "View History" link that lists all evaluations chronologically.
