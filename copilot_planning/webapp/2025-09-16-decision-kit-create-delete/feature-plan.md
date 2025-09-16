# Feature Plan: Decision Kit Create & Cascade Delete

## Problem

Users need to create new decision kits for evaluation workflows and remove obsolete kits. Currently (per prior refactor plan) we can list and view decision kits, but there's no implemented UI flow for creating a kit nor a safe, explicit deletion mechanism. Additionally, deleting a kit must ensure all child entities (rubric association, criteria weights, candidates, candidate materials, reports/assessments) are removed to prevent orphaned data and inconsistent UI state.

## Goals (acceptance criteria)

- User can open a "Create Decision Kit" form (modal or dedicated route) providing name (required) and description (optional).
- Submitting valid form calls API to create kit, navigates to new kit detail page, and displays success feedback.
- Validation: name is required (non-empty after trim, length limit e.g. 100 chars), description length limit (e.g. 1000 chars) with live counter.
- User can delete a decision kit from its detail page via a prominent but safe action (Delete button).
- Delete action requires confirmation (modal) with kit name typed or explicit confirmation checkbox.
- On successful delete: navigate back to kit list, remove kit from list state cache, show toast/snackbar confirming deletion.
- Cascade delete semantics: UI clearly communicates all associated rubric links, criteria weights, candidates, candidate materials, assessments, and reports will be removed.
- Loading / submitting states show progress (disable buttons, spinner) to prevent duplicate actions.
- Errors surface user-friendly messages and allow retry for both create and delete.
- Accessible: form fields labeled, delete confirmation dialog focus-trapped, buttons keyboard operable, ARIA attributes on dialog.

## Non-goals

- Editing existing kits (covered separately).
- Bulk deletion.
- Soft delete / archive states (hard delete only).
- Undo deletion / restore.
- Advanced form fields beyond name/description (no tags, owners, etc.).

## Design

### UX Flow — Create

1. User clicks "New Decision Kit" (from list page header or floating action button).
2. Navigates to `/kits/new` (preferred for consistency with prior refactor plan) OR opens a modal (choose route-first design for deep linking and simpler navigation/back behavior).
3. Form: Name (text), Description (multiline text), Submit, Cancel.
4. Submit triggers POST `/decision-kits`.
5. On success: router push to `/kits/{id}` + success toast; local cache updated to include new kit.
6. On failure: display inline error summary + field-level errors if provided by API.

### UX Flow — Delete

1. User on `/kits/{id}` clicks Delete button.
2. Confirmation dialog opens describing cascade effect; requires explicit confirmation (checkbox or typing kit name — choose checkbox for speed, add typed name pattern as future hardening option).
3. User confirms and clicks "Delete".
4. DELETE `/decision-kits/{id}` call.
5. On success: invalidate/remove kit from cache, navigate to `/`, show toast.
6. On failure: show dialog error message with retry or cancel.

### Components (new / updated)

- `routes/AddDecisionKitPage.tsx` (if not already implemented) or repurpose existing planned Add page.
- `components/decisionKits/DecisionKitForm.tsx` — reusable form (create now, edit future) with validation.
- `components/decisionKits/DeleteDecisionKitDialog.tsx` — confirmation dialog.
- `components/decisionKits/DeleteKitButton.tsx` — button that triggers dialog (may already exist in refactor plan; update for confirmation strategy).
- `hooks/useCreateDecisionKit.ts` — mutation hook (optimistic update optional).
- `hooks/useDeleteDecisionKit.ts` — mutation hook handling cascade messaging.
- Extend existing `useDecisionKits` for cache insertion/removal.

### Data Contracts (frontend assumption)

Create request body:

```ts
{ name: string; description?: string }
```

Create response (kit summary):

```ts
{ id: number; name: string; description?: string }
```

Delete: `204 No Content` or `200` with confirmation payload (assume 204; handle generically).

### Error Handling Strategy

- Validation errors (400) mapped to field errors.
- Generic server errors → toast: "Unable to create decision kit. Please retry.".
- Delete conflict (409) (e.g. if kit locked/complete) → show specific message.
- Not found (404) on delete → treat as already removed; navigate home with warning toast.

### Accessibility

- Form fields with `<label for>` associations and aria-describedby for helper text / counters.
- Dialog uses `role="dialog"` with `aria-modal="true"`, initial focus on dialog heading or first focusable control.
- Escape closes dialog (unless in-flight delete pending).

## Impacted code

- New: `apps/webapp/src/routes/AddDecisionKitPage.tsx` (if absent).
- New: `apps/webapp/src/components/decisionKits/DecisionKitForm.tsx`.
- New: `apps/webapp/src/components/decisionKits/DeleteDecisionKitDialog.tsx`.
- Update: `apps/webapp/src/components/decisionKits/DeleteKitButton.tsx` (wire dialog & hook).
- New: `apps/webapp/src/hooks/useCreateDecisionKit.ts`.
- New: `apps/webapp/src/hooks/useDeleteDecisionKit.ts`.
- Update: `apps/webapp/src/hooks/useDecisionKits.ts` (cache mutation: add/remove).
- Update: `apps/webapp/src/api/decisionKits.ts` (add post/delete functions if missing).
- Possibly update routing in `apps/webapp/src/App.tsx` to include `/kits/new`.

## Edge cases and risks

- Duplicate name submissions: backend may allow; if uniqueness enforced, surface message.
- User double-click submit: disable button while pending to avoid duplicate kit creation.
- Network failure mid-delete: kit may or may not be gone; on retry check if 404 then treat as success with warning.
- Large cascade processing time: show spinner + keep dialog open until completion.
- Stale cache after deletion (other tabs open): out-of-scope; future real-time or polling.

## Test plan

- Unit: form validation (required name, length limits), create hook success/failure, delete hook success/conflict/not-found.
- Component: creating kit navigates to detail with toast.
- Component: deletion removes kit card from list after returning.
- Component: dialog requires confirmation before enabling Delete button.
- Edge: 404 on delete treated as success navigation + warning toast.
- Accessibility: focus trapped in dialog; tab order cycles; ESC closes (when idle).

## Migration/compat

- Adds create/delete flows; no breaking changes to view flows.
- Reusable form sets foundation for future edit feature (name/description update).

## Rollout

- No feature flag needed; integrates with existing Decision Kit list UI.
- Document usage in README (Creating & Deleting Decision Kits section).

## Links

- Decision Kit UI Refactor plan: `copilot_planning/webapp/2025-09-16-decision-kit-ui-refactor/feature-plan.md`
- (Future) Edit feature plan TBD.
