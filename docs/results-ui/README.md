# Results & Authoring UI

## Purpose
Provide a unified interface for defining evaluation criteria and viewing document evaluation results.

## Primary Views
1. Rule Templates
   - List, filter by document type
   - Create / edit / publish workflow
   - Version history panel
2. Ingestion Dashboard
   - Recent uploads + status
   - Retry & re-index actions
3. Evaluation Detail
   - Overall + dimension scores
   - Rule-level findings with rationale & evidence links
4. (Future) Comparison View
   - Multi-doc or multi-template score comparison

## Interaction Model
- Publish flow locks template (creates immutable version)
- Evaluate action selectable from document row (choose template)
- Real-time status polling (or websocket push) for ingestion/evaluation progress

## Component Sketch (React / TS - future)
```
/components
  /rules
    RuleTemplateList.tsx
    RuleTemplateEditor.tsx
  /ingestion
    IngestionTable.tsx
  /evaluation
    EvaluationSummary.tsx
    FindingsTable.tsx
```

## Data Fetch Contracts (Draft)
- GET /rules?documentType=RFP
- GET /rules/{id}
- GET /ingestion?status=indexed
- GET /evaluations/{id}
- POST /evaluate

## UX Considerations
- Show confidence / rationale toggle
- Highlight missing required sections distinctly
- Provide export (JSON first; PDF later)

## Open Questions
- Auth model? (JWT / Entra ID?)
- Dark mode priority?
- Accessibility baseline (semantic HTML + ARIA)

## Next Steps
- Wireframe low-fi screens
- Define component props / data contracts
- Decide on state management (query library vs. global store)
