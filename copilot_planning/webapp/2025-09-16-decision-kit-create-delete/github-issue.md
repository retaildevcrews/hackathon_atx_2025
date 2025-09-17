# GitHub Issue: Decision Kit Create & Cascade Delete

## Summary

Add UI flows to create a new Decision Kit (name + optional description) and delete an existing kit with confirmation. Deletion must cascade removal of all related entities (rubric association, criteria weights, candidates, candidate materials, assessments/reports) to avoid orphans.

## Motivation

Without create/delete, users cannot manage lifecycle of evaluation contexts. Orphaned child entities after a manual backend delete create inconsistent UX, potential storage bloat, and confusion during audits.

## Acceptance Criteria

- [ ] Route `/kits/new` (or accessible create entry) shows form with required name, optional description
- [ ] Name validation: non-empty, trimmed, length <= 100
- [ ] Description length limited (e.g. 1000 chars) with remaining counter
- [ ] Successful create redirects to new kit detail and shows success toast
- [ ] Create error displays inline message and preserves form state
- [ ] Delete button visible on kit detail page
- [ ] Delete opens confirmation dialog describing cascade removal
- [ ] User must check confirmation box (or similar) before Delete enabled
- [ ] Delete shows progress state; success navigates to list and removes kit from UI cache
- [ ] Delete 404 treated as success with warning toast (already removed)
- [ ] Delete 409 (locked/complete) surfaces non-destructive error and does not remove kit
- [ ] Accessibility: dialog focus trap, ESC closes (when idle), labels + aria-describedby on form fields
- [ ] Unit and component tests cover create success/failure and delete flows

## Scope

Included:

- Form route + validation
- Create API integration
- Delete confirmation dialog + API call
- Cache update (add/remove kit entries)
- Toast/snackbar feedback

Excluded / Out of Scope:

- Editing existing kits
- Soft delete or archival
- Undo restore
- Bulk operations

## Design Overview

- Use existing layout and theming
- React Router route `/kits/new`
- `DecisionKitForm` reused for create (future edit)
- `useCreateDecisionKit`, `useDeleteDecisionKit` hooks
- Confirmation dialog with checklist + destructive action styling

## Impacted Code

- `src/routes/AddDecisionKitPage.tsx` (new if absent)
- `src/components/decisionKits/DecisionKitForm.tsx`
- `src/components/decisionKits/DeleteDecisionKitDialog.tsx`
- `src/components/decisionKits/DeleteKitButton.tsx` (update)
- `src/hooks/useCreateDecisionKit.ts`
- `src/hooks/useDeleteDecisionKit.ts`
- `src/hooks/useDecisionKits.ts` (cache insertion/removal)
- `src/api/decisionKits.ts` (add post/delete)
- `src/App.tsx` (route wiring)

## Test Plan

- Form validation (empty name error, length boundaries)
- Create success navigates and toast appears
- Create failure shows inline error retains input
- Delete dialog requires confirmation checkbox
- Delete success removes kit from list
- Delete 404 path treated as success with warning
- Delete 409 shows conflict error, dialog stays open
- Accessibility: focus trapped, tab cycles, ESC closes

## Risks and Mitigations

- Race: user opens dialog then kit deleted elsewhere → handle 404 as success
- Double submission → disable submit while pending
- Long delete cascade → progress spinner; allow cancel only if operation cancellable (else block)
- Cache inconsistency across tabs → acceptable for now

## Definition of Done

- All acceptance criteria satisfied
- Lint/build/tests pass
- Documentation updated (README section on creating & deleting kits)
