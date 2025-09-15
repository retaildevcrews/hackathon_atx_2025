# Azure Resources (Minimal Hackathon Set)

Goal: Only provision what is absolutely needed to demo ingestion, rule-based + LLM evaluation, and results display. Everything else is deferred.

## Required (Provision These)
| Order | Resource | Purpose | Minimal Notes |
|-------|----------|---------|---------------|
| 1 | Resource Group | Logical container | Single RG only (dev) |
| 2 | Storage Account (Blob) | Raw documents (`raw-docs`) | Standard GPv2; public network OK for hack |
| 3 | Azure Document Intelligence | Structured text + layout extraction | Use `prebuilt-layout` model; pay per page |
| 4 | Azure OpenAI | LLM reasoning + embeddings | One reasoning model + one embedding deployment |
| 5 | Azure AI Search | Chunk retrieval (keyword + vector optional) | Basic tier; enable vector if embeddings used |
| 6 | Cosmos DB (Core SQL) | Rules + ingestion status + evaluations | 1 DB, 3 containers (`rules`, `ingestionStatus`, `evaluations`) |
| 7 | Azure Functions (or Container App) | API + ingestion worker + evaluation trigger | Choose Functions Consumption for speed |

## Nice-To-Have (Defer Unless Time Left)
| Resource | Reason to Defer |
|----------|----------------|
| Application Insights | Can use console logs initially |
| Power Automate | Not critical to core evaluation loop |
| Redis Cache | Premature optimization |
| Static Web App | Local dev server fine for UI prototype |
| Key Vault | Inline local dev secrets sufficient short-term |

## Minimal Data Structures
Cosmos Containers:
```
rules (pk: /documentType)
ingestionStatus (pk: /documentId)
evaluations (pk: /documentId)
```

Search Index (fields):
```
id (key)
documentId (filter/search)
section (search)
content (search)
pageRange (filter)
embedding (vector, optional)
metadata (raw JSON string)
```

## Essential Environment Variables
```
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
SEARCH_ENDPOINT=
SEARCH_ADMIN_KEY=
COSMOS_CONN_STRING=
STORAGE_CONN_STRING=
EVAL_TEMPLATE_DEFAULT=rfp_security_pack_v1
```

## Minimal Provisioning Sequence
1. Create Resource Group
2. Create Storage + container `raw-docs`
3. Create Azure Document Intelligence resource (Cognitive Services multi-service)
4. Create OpenAI (apply early if access approval needed)
5. Create Cosmos (DB + containers)
6. Create Search service + index
7. Deploy Functions (API + ingestion trigger + evaluate)

## Thin Architecture Diagram
```
Upload -> Blob -> Function -> Document Intelligence (layout OCR) -> Chunk+Embed -> Search (index)
                                                           |
                                                           v
                                                      Cosmos (status)

Evaluate -> Function -> Cosmos (rules) -> Search (chunks) -> OpenAI (reason) -> Cosmos (evaluation)
```

## Out of Scope (For Now)
- Private networking
- Multi-environment separation
- Advanced monitoring dashboards
- Workflow automation
- Cost optimization beyond obvious (limit model calls)

## Decommission (Manual)
Delete the single resource group when finished.

---
This minimal set keeps focus on delivering end-to-end functionality fast; expand only after first demo success.
