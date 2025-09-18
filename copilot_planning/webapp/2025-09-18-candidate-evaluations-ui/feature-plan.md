# Candidate Evaluations UI — Feature Plan

## Problem

Users can trigger evaluations for candidates (single-candidate evaluation flow already exists), but after an evaluation runs there is no UI surface to (a) discover that evaluations exist for a candidate, (b) quickly view the latest evaluation details, or (c) see at-a-glance the most recent score while browsing candidates in a decision kit. This creates a blind spot: users re-run evaluations unnecessarily and cannot compare or validate the most recent outcome.

## Goals (acceptance criteria)

- When loading a decision kit detail page, if a candidate has ≥1 evaluation, its tile shows the latest evaluation score (overall_score) as a compact badge or subtext.
- A "View Evaluations" (or "Latest Evaluation") button is conditionally shown (one per candidate tile OR a unified candidate detail action) only if that candidate has ≥1 evaluation.
- Clicking the button navigates to a dedicated page: `/decision-kits/:kitId/candidates/:candidateId/evaluations/latest` (or `/evaluations` then auto-load latest) that displays the latest evaluation for that candidate.
- Latest evaluation page shows: rubric name, evaluation timestamp, overall_score, and the candidate-specific breakdown if available (individual candidate result slice: score, rank if present, and any per-criteria details derivable from `individual_results`).
- If evaluation data is loading, show skeletons; if none found (race condition), show a not-found friendly state with link back.
- If multiple evaluations exist, latest is determined by `created_at` (newest). No sorting ambiguity.
- Evaluation fetch errors show a retry option.
- No change to existing evaluation trigger button (Evaluate) besides optionally refreshing the candidate evaluation badge post-run.

## Non-goals

- Historical evaluation list UI (beyond latest) — could be future enhancement.
- Visualization/graphs of score evolution over time.
- Batch comparison UI (is_batch true case) for multiple candidates side-by-side.
- Editing or deleting evaluation results from this UI.

## Design

### Data Flow

1. Decision kit detail already loads kit + candidates. To avoid N+1 fetches on first render, evaluation presence can be lazy: when candidate tiles mount, issue parallel fetches to `/candidates/{id}/evaluations` (summaries). Cache results client-side (simple in-memory map keyed by candidateId) to minimize repeat requests on navigation.
2. For each candidate: fetch summaries (List[EvaluationResultSummary]). Determine latest by max `created_at`.
3. Store latest summary (id + overall_score + created_at + rubric_name) in state. Display small badge (e.g., Chip variant) reading `Score: 4.2` (1 decimal) or `4.2 ★`.
4. Button: If summary list length > 0 show small "View Eval" text button.
5. Clicking navigates to latest evaluation details route. That route uses evaluation id to call `/candidates/evaluations/{evaluation_id}` (full model) OR reuse summaries list in parent and only fetch full detail if not already cached.

### UI Elements

- Candidate Tile additions:
  - Score badge below description (Typography variant="caption" / Chip color=primary; tooltip with timestamp, rubric name).
  - Small text button (size="small") aligned with existing Evaluate button or placed adjacent.
- Latest Evaluation Page:
  - Breadcrumb: Decision Kit Name / Candidate Name / Latest Evaluation
  - Header: Candidate Name + Overall Score (large)
  - Subheader: Rubric Name, Evaluated at <relative time>.
  - Section: Criteria Breakdown (if `individual_results` has per-criteria scoring for this candidate). Need to inspect structure: we expect `individual_results` list with candidate associations; filter entry for candidate id.
  - Fallback message if breakdown not available.
  - Back button to decision kit page.

### Types & API

Add webapp API helpers:

- `fetchCandidateEvaluations(candidateId): Promise<EvaluationResultSummary[]>`
- `fetchEvaluationResult(evaluationId): Promise<EvaluationResult>`
Optional caching layer similar to decisionKit detail maps.

### State Management / Performance

- Use simple module-level Maps (not introducing heavy state libs) mirroring existing pattern (`decisionKits.ts` caches detail). Map keys: `candidateId -> { summaries, fetchedAt }`; `evaluationId -> fullEvaluation`.
- Avoid blocking kit page initial paint; load evaluations after main content via `useEffect` with abort support.

### Accessibility

- Score badge has `aria-label` describing last evaluation score and timestamp.
- Button text clear: "View Evaluation" (singular) since only showing latest.

### Error Handling

- Per-candidate evaluation summary fetch failure: show unobtrusive warning icon with tooltip; allow retry icon button (optional, stretch) or auto retry once.
- Latest evaluation page network error: full-width Alert with retry.

## Impacted code

- `apps/webapp/src/pages/decision-kits/DecisionKitDetailPage.tsx`: augment candidate tiles to load and display latest evaluation badge + view button.
- `apps/webapp/src/api/evaluations.ts` (new): add fetch functions for summaries & detail.
- `apps/webapp/src/hooks/useCandidateEvaluations.ts` (new) or inline logic; prefer hook for reuse/testing.
- `apps/webapp/src/pages/candidates/CandidateLatestEvaluationPage.tsx` (new) route page.
- `apps/webapp/src/pages/App.tsx` (routing): add new route path.
- `apps/webapp/src/types/evaluations.ts` (new): TypeScript interfaces mirroring backend models (Summary & Full).
- Possibly `apps/webapp/src/components/evaluations/CandidateEvaluationDetail.tsx` (new) to render breakdown.

## Edge cases and risks

- Large number of candidates causes many parallel summary calls (N). Mitigation: throttle concurrency (optional), or lazy load only on expand/collapse (already gated by candidatesOpen). Could batch endpoint in backend later.
- Race: evaluation triggered then summaries load before evaluation persisted — acceptable; user can manually retry evaluation fetch (score simply absent initially).
- Timezone formatting consistency — use existing date util or `toLocaleString` with fallback.
- EvaluationResult structure may not include per-candidate detailed breakdown easily; if `individual_results` shape ambiguous, show only overall score + metadata until richer mapping defined.
- Backend pagination for candidate evaluations not implemented; endpoint returns full list — assume manageable size short-term.

## Test plan

- Unit: API helpers resolve and map fields, error propagation when HTTP 404/500.
- Component: Candidate tile shows score badge after successful fetch; hides button when zero results; shows button when ≥1.
- Page: Latest evaluation page renders overall score, rubric name, timestamp.
- Error: Simulate fetch failure -> Alert + retry restores success.
- Edge: Two evaluations with different timestamps -> latest chosen (verify ordering logic).

## Migration/compat

- Fully additive; no breaking changes. If backend endpoints change, only new frontend code affected.
- Caching ephemeral; no persistence across reloads.

## Rollout

- No feature flag; small incremental UI.
- Monitor network calls count for candidate-heavy kits (dev tools) — consider backend aggregation later.

## Links

- Existing evaluation trigger flow in `DecisionKitDetailPage` (`evaluateCandidates`).
- Backend evaluation endpoints in `candidates.py` (get candidate evaluations, get evaluation result by id).
