# Results & Authoring UI

> **Status:** Active development – decision kits list/detail and rubrics list/detail/edit pages implemented; full rule template authoring and comparison views are future.

## Purpose

Provide a unified interface for defining evaluation criteria and viewing document evaluation results.

## Primary Views (Current vs. Planned)

| View | Current State | Future Enhancements |
|------|---------------|---------------------|
| Decision Kits List | Implemented | Sorting, filtering, bulk actions |
| Decision Kit Detail | Implemented (candidates, attach rubric) | Side-by-side candidate comparison |
| Rubrics List | Implemented | Tag filtering, search |
| Rubric Detail | Implemented | Historical version diff |
| Rubric Create/Edit | Implemented (basic fields) | Advanced weight editor, validation hints |
| Rule Template Authoring | Not yet (uses rubrics flow) | Dedicated builder with live preview |
| Evaluation Detail | Placeholder / emerging | Findings table w/ evidence linking |
| Ingestion Dashboard | Not implemented | Status + retry controls |
| Comparison View | Not implemented | Multi-rubric or multi-candidate compare |

## Interaction Model (Evolving)

- Navigation drawer provides persistent access to Decision Kits & Rubrics.
- Light/dark theme toggle in AppBar.
- Sidebar collapsible on desktop & mobile.
- Future: inline rubric weight adjustments with immediate scoring preview.

## Component Sketch (Indicative – Will Evolve)

```text
src/components/
   navigation/NavigationDrawer.tsx
   decisionKits/DecisionKitForm.tsx
   decisionKits/DeleteDecisionKitDialog.tsx
   rubrics/RubricForm.tsx (future restructuring)
   AttachRubricForm.tsx
```

## Data Fetch Contracts (Current / Planned)

| Endpoint | Status | Notes |
|----------|--------|-------|
| GET /criteria (or /rubrics) | Implemented | List rubrics (naming may evolve) |
| GET /criteria/{id} | Implemented | Retrieve rubric detail |
| POST /criteria | Implemented | Create rubric |
| PUT /criteria/{id} | Implemented | Update rubric |
| GET /decision-kits | Implemented | List decision kits |
| GET /decision-kits/{id} | Implemented | Detail with attached rubric + candidates |
| POST /decision-kits | Implemented | Create kit |
| DELETE /decision-kits/{id} | Implemented | Delete kit |
| POST /decision-kits/{id}/candidates | Implemented | Add candidate |
| (Future) GET /evaluations/{id} | Planned | Structured evaluation output |
| (Future) POST /evaluate | Planned | Trigger evaluation run |

## UX Considerations

- Keep left navigation minimal; rely on contextual actions in pages.
- Provide progressive disclosure for advanced rubric settings.
- Ensure mobile layout retains full-width header for consistency.
- Future: export evaluation results (JSON first).

## Open Questions

- Auth integration timeline (Entra ID vs. local dev only?)
- How to visualize rubric weight impact dynamically?
- Best placement for evaluation run status (toast vs. inline panel)?

## Next Steps

- Refactor rubric form into domain folder
- Add evaluation detail placeholder page
- Introduce search / filter in Rubrics List
- Persist sidebar collapsed state in localStorage
