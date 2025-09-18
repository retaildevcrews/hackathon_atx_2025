# RubricX

_Define what matters, decide what wins._

RubricX is designed to revolutionize how organizations evaluate proposals, documents, and other inputs against explicit, configurable criteria. Inspired by real conversations with procurement and innovation teams, it targets the pervasive problem of subjective, opaque, and inconsistent evaluations. RubricX makes evaluation rules transparent, adaptable, and auditable—reducing friction, accelerating decisions, and improving trust.

While the concept originated in enterprise procurement and innovation governance, rubric‑based, criteria‑driven evaluation applies far beyond the enterprise: grant proposal reviews, classroom/project assessment, startup pitch scoring, hiring packet and promotion dossier review, compliance readiness, open source project triage, community budget allocation—even decidedly personal or consumer choices like comparing televisions, selecting a home espresso setup, evaluating conference talk submissions, or prioritizing backyard renovation ideas. Anywhere decisions benefit from explicit criteria, weighted scoring, and transparent rationale—RubricX can help.

## What It Does (At a Glance)

- Ingests and analyzes inputs (e.g., RFPs, RFQs, internal proposals)
- Applies configurable rubrics (criteria, weights, thresholds)
- Produces structured scores, rationale, gaps, and risk flags
- Supports iterative refinement of criteria over time
- Maintains an auditable trail of how and why decisions were made

## Why It Matters

Current evaluation processes are often:

- Tribal (implicit criteria)
- Inconsistent (varies by reviewer)
- Slow (manual cross-document checks)
- Hard to audit (little rationale captured)

RubricX addresses this by combining deterministic rule checks with AI-assisted analysis over indexed content, producing explainable outputs aligned to organization-defined standards.

## Core Pillars

- Explicit Criteria: Make standards first-class, not folklore
- Configurable Rubrics: Adapt to domain, maturity, and context
- Transparent Scoring: Show how each score was produced
- Actionable Insights: Highlight risks, omissions, and recommendations
- Auditability: Preserve rationale and versioned rule sets
- Extensibility: Designed for new document types and workflows

## Getting Started

Minimal bootstrap using Docker Compose:

1. Copy example environment files:

   ```bash
   cp apps/agent/.env.example apps/agent/.env
   cp apps/criteria_api/.env.example apps/criteria_api/.env
   ```

1. Edit `apps/agent/.env` and set required values:

   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_DEPLOYMENT`
   - (Optional / if search used) `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_API_KEY`, `AZURE_SEARCH_INDEX`
   - Leave `CRITERIA_API_URL` as `http://criteria_api:8000` when using Compose (or localhost outside Compose)

1. Edit `apps/criteria_api/.env` with Cosmos DB credentials:

   - `COSMOSDB_ENDPOINT`
   - `COSMOSDB_KEY`
   - (Defaults for `COSMOSDB_DATABASE` / `COSMOSDB_CONTAINER` are acceptable initially)

1. Start the stack:

   ```bash
   cd apps
   docker compose up --build
   ```

1. Open the web UI (typically `http://localhost:5173`) and begin configuring criteria.

For deeper flows (index seeding, evaluation orchestration details), see the docs.

## Documentation

For architecture, design artifacts, roadmap, data models, and deeper technical context see:

➡️ `docs/README.md`

## Status

Early-stage hackathon-originated prototype evolving toward a more general evaluation platform. Expect rapid iteration and refactors.

## Contributing

Open an issue or small PR; keep scope focused. See documentation for emerging conventions.

---
Historic, in-depth planning content from the original hackathon README has been moved into the documentation set to reduce noise at the top level.
A: Provides a standardized way to expose tools (retrieval, rule evaluation, workflow triggers) to AI agents.

Q: Do we support image-based PDFs?
A: Via Document Intelligence OCR (planned if time permits).

## License

TBD (add a LICENSE file if/when determined).

---
