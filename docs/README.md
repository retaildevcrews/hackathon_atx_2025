# RubricX Documentation

This `docs/` folder contains deeper design notes, conceptual schemas, and forward-looking plans. The top-level README intentionally stays concise; detailed evolution lives here.

## Current Scope vs. Vision

| Area | Current State (Prototype) | Future / Stretch |
|------|---------------------------|------------------|
| Criteria / Rubric Service | Basic criteria API (Cosmos model draft) | Versioning, publishing workflow, validation tooling |
| Agent / Evaluation | Hybrid evaluation scaffolding with Azure OpenAI + planned search integration | Deterministic + semantic retrieval orchestration, cost optimization heuristics |
| UI | Rubrics & decision kits management views | Full template authoring, evaluation dashboards, comparisons |
| Ingestion / Indexing | Stub / manual data seeding | Automated extraction, chunking, Azure AI Search index pipeline |
| Auditability | Basic logging | Full rationale graph + provenance store |

## Workstream Docs

| Workstream | Path | Purpose |
|------------|------|---------|
| Evaluation Criteria Authoring & Rule Store | `./evaluation-criteria/` | Rule template schema, versioning approach, API surface |
| Document Ingestion & Indexing | `./ingestion-indexing/` | Proposed extraction + indexing pipeline (future) |
| Analysis Agent & Structured Evaluation | `./analysis-agent/` | Evaluation flow (rules + LLM), output contract |
| Results & Authoring UI | `./results-ui/` | UI views, component plans, interaction model |

Each subfolder captures the intended direction. Where something is not yet implemented, it is still retained to guide incremental build-out.

## Contributing to Docs

When updating implementation details, prefer:

1. Adjust schema / contract examples alongside code changes.
2. Mark removed ideas with a brief rationale instead of deleting when still instructive.
3. Use callouts like `> **Status:** future` for speculative sections.

## Glossary (Seed)

| Term | Definition |
|------|------------|
| Rubric | A structured set of criteria with weights and guidance used to evaluate an input. |
| Criterion | Individual evaluative element (may map to a dimension). |
| Dimension | Aggregated scoring axis grouping related criteria. |
| Evaluation | Result record containing per-rule findings, scores, and rationale. |

## Next Documentation Enhancements

- Add sequence diagram for evaluation agent once retrieval step is wired
- Provide sample rubric JSON aligned to current API models
- Introduce decision kit concept doc when stabilised

---
Feedback and PRs welcome—keep docs close to the code reality while signaling the near-term path.
