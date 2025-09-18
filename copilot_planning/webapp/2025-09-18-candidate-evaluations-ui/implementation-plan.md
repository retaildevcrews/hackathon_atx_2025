# Implementation Plan — Candidate Evaluations UI

## Pre-flight

- [ ] Confirm backend endpoints:
  - [x] `/candidates/{candidate_id}/evaluations` returns `EvaluationResultSummary[]` (verified in `candidates.py`).
  - [x] `/candidates/evaluations/{evaluation_id}` returns full `EvaluationResult`.
- [ ] Identify structure of `individual_results` for candidate-specific breakdown (inspect a sample response; if unavailable, render basic metadata only). *Action:* add conditional rendering placeholder.
- [ ] Decide route naming: use `/decision-kits/:kitId/candidates/:candidateId/evaluations/latest`.
- [ ] No new dependencies needed (reuse axios, MUI).

## Implementation

- [ ] Add `types/evaluations.ts`
  - `EvaluationResultSummary` (fields: id, rubric_id, rubric_name, overall_score, total_candidates, is_batch, created_at)
  - `EvaluationResult` (full model + candidates array + individual_results)
  - `EvaluationCandidate` (id, evaluation_id, candidate_id, candidate_score, rank?, created_at)
- [ ] Add `api/evaluations.ts`
  - `fetchCandidateEvaluations(candidateId)`
  - `fetchEvaluationResult(evaluationId)` with mapping & error normalization (similar to `candidates.ts` pattern)
- [ ] Add hook `useCandidateEvaluations(candidateId)`
  - Internal cache Map; fetch on mount; expose `latest`, `summaries`, `loading`, `error`, `retry`.
  - Determine latest via max created_at.
- [ ] Update `DecisionKitDetailPage.tsx`
  - Import hook per candidate tile (careful to avoid calling hooks in loops — instead create a child component `CandidateTile` that uses the hook).
  - Display score badge (Chip or Typography caption) when `latest` present.
  - Show `View Eval` button linking to latest evaluation page when present.
- [ ] Add page `CandidateLatestEvaluationPage.tsx`
  - Params: kitId, candidateId.
  - On mount: fetch summaries if not cached; identify latest; fetch full evaluation detail (if not cached) using id.
  - Render: overall score prominent, rubric name, created_at formatted, candidate-specific breakdown (filter candidate id in evaluation.candidates or within individual_results if necessary).
  - Back button to `/decision-kits/:kitId`.
- [ ] Add route in `App.tsx` for latest evaluation page.
- [ ] Add component `CandidateEvaluationDetail.tsx` for rendering detail (props: evaluation, candidateId) — optional separation for clarity.
- [ ] Post-evaluate action (in existing Evaluate button) triggers refresh of candidate evaluations (invalidate cache entry for candidateId and re-fetch).

## Validation

- [ ] Unit test `api/evaluations.ts` (mock axios): success + 404 + 500.
- [ ] Unit test hook logic (using React Testing Library): latest selection when two summaries.
- [ ] Component test: Candidate tile shows badge and button after mock fetch.
- [ ] Page test: Latest evaluation page renders score and rubric name.
- [ ] Error test: simulate failure -> shows retry.

## Samples and documentation

- [ ] Update webapp README (brief section: Candidate Evaluations UI, route, behavior).
- [ ] Link feature plan in planning index if maintained.

## Rollout

- [ ] Manual QA: trigger evaluation, refresh kit page, verify badge appears.
- [ ] Confirm no runtime errors when no evaluations (hook returns empty state; no button/badge).
- [ ] Monitor network request count (log in dev console) for candidate-heavy kits.

## Post-launch (future enhancements, not in scope)

- Historical evaluations list & navigation.
- Trend chart (score over time).
- Batch evaluation comparison table per rubric.
