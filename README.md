# Veda.AI (hackathon_atx_2025)

Accelerating document-centric workflows through configurable AI-driven analysis. This repo contains artifacts for the Global Hackathon 2025 (Crew ATX @ Redmond) focused on building an extensible evaluation and insight engine for complex business documents.

## Hack Objectives
1. Learning & Enablement
	- Leverage GitHub Copilot to accelerate the development process
	- Explore agentic patterns (e.g., Model Context Protocol - MCP) for tool orchestration
2. Functional Prototype
	- Ingest and analyze documents (RFPs, RFQs, idea proposals, etc.)
	- Assess adherence to configurable guidelines and evaluation criteria
	- Generate actionable insights (gaps, risks, recommendations)
3. Extensibility
	- Pluggable rule definitions & scoring logic per domain
	- Support multiple document types and evaluation templates
4. Evaluation Methodology Exploration
	- Investigate evaluation approaches for system quality (rule coverage, precision/recall on findings, scoring stability)
	- Define lightweight benchmarking harness using sample labeled documents
	- Track cost vs. quality trade-offs across prompt strategies / model selections

## Problem Statement
Organizations spend significant time manually reviewing structured and semi-structured documents (procurement specs, internal proposals, vendor responses). Reviews are inconsistent, slow, and dependent on tribal knowledge. Veda.AI automates the first-pass evaluation and surfaces high-value insights early.

## Core Value Proposition
Turn unstructured documents into structured evaluations with: gaps detected, risks flagged, scores assigned, and recommendations generated—while allowing teams to define their own domain rules.

## Key Features
| Category | Capability | Notes |
|----------|------------|-------|
| Document Ingestion | Accept PDF, DOCX, TXT | Future: spreadsheet + HTML |
| Content Extraction | Azure AI Document Intelligence / Azure Cognitive Search indexing | Normalizes structure & sections |
| AI-Powered Analysis | Azure OpenAI + retrieval over indexed chunks | Context-aware reasoning |
| Gap & Risk Detection | Rule + LLM hybrid | Highlights omissions & ambiguities |
| Custom Evaluation Engine | Configurable YAML/JSON templates | Domain-specific criteria |
| Scoring & Weighting | Composite scores per dimension | Supports threshold alerts |
| Insight Generation | Summaries, missing elements, risk flags | Exportable summary objects |
| Workflow Integration | Power Automate / Webhook triggers | Notifications & escalations |
| Explainability | Traceable rationale per finding | LLM response + rule reference |
| Agentic Orchestration (Stretch) | MCP tools for retrieval, rule evaluation, workflow callbacks | Modular tool registry |

## Representative Use Cases
1. RFQ/RFP Analyzer
	- Flags missing security, compliance, pricing, SLA, or support model elements
	- Scores alignment to internal standards
2. Idea / Proposal Analyzer
	- Evaluates feasibility, completeness, strategic fit
	- Highlights unclear assumptions, missing metrics, or unmitigated risks
3. Policy Conformance Check (Future)
	- Validates internal policy adherence (e.g., data handling, accessibility)
4. Vendor Response Compare (Future)
	- Side-by-side scoring across multiple submissions

## Architecture (Proposed)
```
User Upload -> Ingestion Layer -> Storage (Blob) -> Extraction & Chunking -> Index (Azure Cognitive Search)
																	  |
																	  v
											  Rule Engine <-> Orchestrator / Agent (MCP)
																	  |
														Azure OpenAI Analysis
																	  |
															Insight Aggregator
																	  |
														Output APIs / UI / Workflow
```

### Components
- Ingestion Service: Validates + stores files; normalizes metadata
- Extraction Pipeline: Uses Azure services to structure text & sections
- Index + Retrieval: Embeddings + search over enriched chunks
- Rule Engine: Deterministic checks (presence, pattern, threshold, taxonomy mapping)
- LLM Reasoning Layer: Contextual interpretation + summarization
- Orchestrator / Agent: Coordinates tools (retrieval, rules, scoring, summarization, workflow triggers)
- Insight Aggregator: Merges rule + LLM outputs; assigns scores; builds explanation graph
- Delivery: REST endpoints, possible lightweight UI, Power Automate connectors (webhook-based)

## Tech Stack (Initial Targets)
| Layer | Choice (Draft) | Notes |
|-------|----------------|-------|
| Language | Python / TypeScript (TBD) | Rapid prototyping + strong ecosystem |
| AI Services | Azure OpenAI | GPT-4.x / o series for reasoning |
| Search / Index | Azure Cognitive Search | Hybrid semantic + keyword |
| Extraction | Azure AI Document Intelligence | Structure & layout parsing |
| Storage | Azure Blob Storage | Raw + processed artifacts |
| Orchestration | MCP-compatible agent + custom tools | Extensible tool registry |
| Config | YAML / JSON templates | Domain rule packs |
| Workflow | Power Automate / Webhooks | Event-driven notifications |

## Evaluation Rule Template (Concept)
Example (YAML-like):
```yaml
id: rfp_security_encryption
category: security
applies_to: ["RFP", "RFQ"]
check: presence
target_section: ["Security", "Data Protection"]
require_keywords: ["encryption", "AES", "TLS"]
severity: high
weight: 0.15
remediation_hint: "Specify algorithms, key rotation policy, and data at rest/in transit coverage."
```

## Sample Output (Concept)
```json
{
  "documentId": "rfp_2025_0042",
  "overallScore": 0.82,
  "dimensions": {
	 "security": 0.74,
	 "completeness": 0.88,
	 "strategic_alignment": 0.90
  },
  "findings": [
	 {
		"id": "rfp_security_encryption",
		"status": "partial",
		"missing": ["key rotation policy"],
		"riskLevel": "high",
		"explanation": "Encryption mentioned but lacks lifecycle details.",
		"recommendation": "Add rotation interval and certificate management process."
	 }
  ],
  "summary": "Document is broadly aligned; primary gaps in security operational detail."
}
```

## Planned Experiments
- Prompt strategies: rule-first vs. retrieval-first vs. hybrid
- Compression of large documents (window management)
- Chain-of-thought retention vs. distilled rationale storage
- Agent tool performance benchmarking

## Roadmap (Hackathon Scope vs Future)
| Phase | Scope | Status |
|-------|-------|--------|
| Day 1 | Repo setup, baseline ingestion flow | Planned |
| Day 2 | Basic extraction + retrieval prototype | Planned |
| Day 3 | Rule engine skeleton + sample rules | Planned |
| Day 4 | LLM analysis + merged insights | Planned |
| Day 5 | Power Automate webhook + demo script | Planned |
| Post | UI polish, multi-doc comparison, benchmarking | Future |

## Workstreams & Deliverables
Four coordinated workstreams compose the prototype. Each can progress semi-independently with lightweight contracts between them.

### 1. Evaluation Criteria Authoring & Rule Store
Purpose: Allow users to define, version, and manage evaluation criteria (rules, scoring weights, templates) per document type.

Scope:
- UI module for creating/editing rule templates (sections, required elements, keyword sets, scoring weights, severity levels)
- Persist templates to Cosmos DB (container: `rules`, partition key: `/documentType`)
- Versioning strategy (e.g., semantic `version` field or timestamp-based)
- Exposure of rule retrieval API for agent consumption (filtered by document type + version)

Data Model (initial sketch):
```
{
	id: "rfp_security_pack_v1",
	documentType: "RFP",
	version: "1.0.0",
	dimensions: ["security", "completeness", "alignment"],
	rules: [
		{
			id: "rfp_security_encryption",
			category: "security",
			check: "presence",
			targetSection: ["Security", "Data Protection"],
			requireKeywords: ["encryption", "AES", "TLS"],
			weight: 0.15,
			severity: "high",
			remediationHint: "Specify algorithms and key rotation."
		}
	],
	scoring: { aggregation: "weighted_sum" },
	createdUtc: "2025-09-15T00:00:00Z",
	createdBy: "user@org"
}
```

Acceptance Criteria:
- User can create and save a rule template
- Retrieval endpoint returns template under 200 ms (local dev target)
- Templates are immutable post-publish (new version required for edits)

Open Questions:
- Need soft vs. hard delete?
- Multi-tenant partitioning needed?
- Rule dependency support (e.g., conditional checks)?

### 2. Document Ingestion & Indexing
Purpose: Accept documents, persist raw artifacts, extract text, and index for retrieval and later analysis.

Assumptions:
- Documents dropped into an Azure Blob Storage container (`raw-docs`)
- Event or scheduled indexer monitors new blobs
- Azure AI Search index (name: `docs-index`) stores chunks + metadata
- Maintain ingestion history and status in Cosmos DB container `ingestionStatus` (partition key `/documentId`)

Ingestion Status Record (sketch):
```
{
	id: "rfp_2025_0042",
	fileName: "RFP_CustomerPortal_v4.pdf",
	blobPath: "rfps/2025/RFP_CustomerPortal_v4.pdf",
	documentType: "RFP",
	sizeBytes: 534221,
	status: "indexed", // uploaded | extracting | indexing | indexed | error
	chunkCount: 142,
	error: null,
	lastUpdatedUtc: "2025-09-15T02:10:00Z"
}
```

Acceptance Criteria:
- New blob triggers extraction + indexing within target SLA (e.g., < 2 min for medium doc)
- Status endpoint surfaces progress
- Re-ingest of identical file (hash) is idempotent

Open Questions:
- Deduplication strategy (hash vs. filename)
- Large doc splitting heuristics (token vs. sentence vs. layout)

### 3. Analysis Agent & Structured Evaluation
Purpose: Given an indexed document and selected criteria template, produce structured evaluation output.

Flow:
1. Fetch rule template from Cosmos
2. Retrieve relevant chunks (per rule or per dimension)
3. Hybrid evaluation: deterministic rule checks + LLM reasoning
4. Aggregate dimension scores + overall composite
5. Persist evaluation result (Cosmos `evaluations` container)

Evaluation Output (sketch):
```
{
	id: "eval_rfp_2025_0042_v1",
	documentId: "rfp_2025_0042",
	ruleTemplateId: "rfp_security_pack_v1",
	overallScore: 0.82,
	dimensionScores: { security: 0.74, completeness: 0.88, alignment: 0.90 },
	findings: [ /* rule-level objects with status, rationale, recommendation */ ],
	createdUtc: "2025-09-15T03:05:00Z"
}
```

Acceptance Criteria:
- Produces JSON output with dimension + rule scores
- Includes rationale text for each non-passing rule
- Handles missing sections gracefully (marked as not found vs. error)

Open Questions:
- Caching retrieval per dimension?
- Cost controls (model selection heuristics)?
- Partial evaluation retries on failure?

### 4. Results & Authoring UI
Purpose: Unified front-end for (a) defining criteria and (b) viewing evaluation results.

Views:
- Rule Template List & Editor
- Document Ingestion Status Dashboard
- Evaluation Run Detail (scores, findings, rationale)
- Comparison (future) across evaluations or templates

Acceptance Criteria:
- Create/edit/publish rule template workflow
- Display evaluation summary + drill-down to per-rule rationale
- Refresh ingestion/evaluation status without page reload (poll or websocket)

Open Questions:
- Role-based access needed?
- Export formats (JSON, CSV, PDF report)?
- Multi-select compare out of scope for hack?

### Cross-Cutting Concerns
- Observability: minimal structured logs (ingestion transitions, agent timing, error taxonomy)
- Security: limit PII retention; ensure least-privileged access to storage/index
- Config: central config file for service endpoints and resource names
- Testing: sample fixture docs + mock rule template + golden evaluation output

### Interfaces (Initial Contracts)
- GET /rules/{documentType}/{version}
- POST /rules (draft) -> publish endpoint
- GET /ingestion/{documentId}/status
- POST /ingestion/scan (optional manual trigger)
- POST /evaluate { documentId, ruleTemplateId }
- GET /evaluations/{evaluationId}

### Suggested Repo Structure (Forward Looking)
```
docs/
services/
	rule-authoring/
	ingestion/
	agent/
	ui/
infrastructure/
samples/
```

Each workstream now has a placeholder directory under `docs/` for deeper specs.

## Stretch Goals
- Cost-aware routing (cheap vs. premium model usage)
- Hallucination mitigation (cross-check rule vs. LLM claims)
- Explainability graph visualization
- Self-updating rule suggestions (LLM proposes new candidate checks)

## Contributing (Hackathon Mode)
Lightweight flow:
1. Create a branch: feature/<short-description>
2. Keep changes small & meaningful
3. Use Copilot / pair prompts for acceleration
4. Open PR with a concise summary + screenshot / sample output when relevant

## Security & Data Handling
- Assume all uploaded documents are sensitive; no external logging of raw content
- Consider content filtering / redaction stage (Future)
- Avoid storing full LLM reasoning unless needed for auditability

## Deployment Notes (Future)
- Containerized services (single compose for prototype)
- Azure resources: OpenAI, Cognitive Search, Blob Storage, (optional) Functions for webhooks
- Observability: minimal logs + latency / token usage metrics

## FAQ (Early)
Q: Is this production-ready?
A: No—hackathon prototype; design aims at future hardening.

Q: Why MCP?
A: Provides a standardized way to expose tools (retrieval, rule evaluation, workflow triggers) to AI agents.

Q: Do we support image-based PDFs?
A: Via Document Intelligence OCR (planned if time permits).

## License
TBD (add a LICENSE file if/when determined).

---
Let us know if you want a lightweight UI scaffold, CLI prototype, or to prioritize rule packs first.
