# Implementation Plan — Decision Kit Create & Cascade Delete

## Pre-flight

- [ ] Confirm existing decision kit list & detail routing structure (ensure `/kits/new` not conflicting)
- [ ] Verify axios API client pattern; extend `api/decisionKits.ts`
- [ ] Decide confirmation UX (checkbox vs typed name) → use checkbox first iteration
- [ ] Determine toast/snackbar mechanism (existing provider or add one)

## Implementation

### Create Flow

- [ ] Add route `/kits/new` in `App.tsx`
- [ ] Add `AddDecisionKitPage.tsx` with container + `DecisionKitForm`
- [ ] Implement `DecisionKitForm` (fields, validation, submit handler props)
- [ ] Hook `useCreateDecisionKit` (POST /decision-kits) returning { mutate, loading, error }
- [ ] On success: update `useDecisionKits` cache (prepend new kit), navigate to detail, show toast
- [ ] Handle validation errors mapping server response

### Delete Flow

- [ ] Implement `useDeleteDecisionKit` (DELETE /decision-kits/:id) with status + error
- [ ] Build `DeleteDecisionKitDialog` (props: open, onClose, onConfirm, pending, error)
- [ ] Enhance `DeleteKitButton` to open dialog
- [ ] Add confirmation checkbox gating destructive action
- [ ] On success: remove kit from cache, navigate to `/`, toast success
- [ ] Handle 404 as success (warn) and 409 as conflict error

### Shared / Utilities

- [ ] Extend `api/decisionKits.ts` with `createDecisionKit`, `deleteDecisionKit`
- [ ] Add form validation util (trim, length bounds) with reusable messages
- [ ] Add toast helper if not existing (context provider or simple event bus)

## Validation (Testing)

- [ ] Unit: validation utils (empty, length overflow)
- [ ] Unit: hooks (mock axios) for success, server error, 404 delete, 409 delete
- [ ] Component: create form error display & navigation on success
- [ ] Component: delete dialog enable/disable of Delete button
- [ ] Component: cache removal after delete (list re-renders w/out kit)
- [ ] Accessibility: dialog focus test (initial focus, tab wrap)

## Documentation

- [ ] README update: Creating & Deleting a Decision Kit section
- [ ] Add notes on cascade semantics and irreversible nature

## Rollout Steps

1. Implement API functions
2. Add hooks (create/delete)
3. Create form + page
4. Wire create route & toast on success
5. Add delete dialog + button integration
6. Update cache logic (add/remove)
7. Write tests
8. Update docs

## Post-merge Follow-ups (Future)

- Typed name deletion confirmation if needed for high-value kits
- Soft delete / archival states
- Optimistic create with rollback on failure
- Bulk operations

## Completion Criteria

- All checklist items above are complete
- Tests pass consistently
- No console errors; lint clean
