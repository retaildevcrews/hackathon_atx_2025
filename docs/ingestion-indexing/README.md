# Document Ingestion & Indexing

## Purpose
Automate ingestion of uploaded documents, extraction of content, and indexing for retrieval.

## Flow
1. User uploads / drops file into blob container (`raw-docs`).
2. Ingestion watcher (timer or event) detects new blob.
3. Extraction service parses text + structure:
   - Primary: Azure AI Document Intelligence (general document + layout model)
   - Optional: Form Recognizer prebuilt (invoices/contracts) if doc type recognized
   - Fallback: Basic PDF/DOCX text extractor (for cost control or outages)
4. Chunker splits into retrieval-sized units (semantic + layout aware).
5. Azure AI Search index updated (index name: `docs-index`).
6. Ingestion status updated in Cosmos DB (`ingestionStatus` container).

### Azure Document Intelligence Integration
| Aspect | Choice / Notes |
|--------|----------------|
| Model | `prebuilt-layout` (captures text, tables, titles, reading order) |
| Invocation | Async API (polling) to handle large PDFs |
| Table Handling | Store raw markdown/CSV in `metadata.tables` (optional) |
| Figures / Images | Placeholder references (future OCR enrich) |
| Confidence Scores | Persist average + min per chunk for quality filtering |
| Cost Optimization | Skip layout if plain-text DOCX < size threshold |

### Enrichment Pipeline (Optional Stages)
1. Raw extraction (layout model output)
2. Structural normalization (merge tiny lines, keep headings)
3. Section inference (regex + heading heuristics + ML later)
4. Key phrase / entity extraction (future: Azure Language)
5. Embedding generation (Azure OpenAI embedding model) stored inline or side store

### Failure & Retry Strategy
| Failure Type | Handling |
|--------------|----------|
| Transient API timeout | Exponential backoff (max 3 attempts) |
| Unsupported format | Mark status `error` with code `UNSUPPORTED_FORMAT` |
| Layout parsing partial success | Index successful pages; flag `partial=true` in metadata |
| Duplicate (hash match) | Short-circuit; optionally re-use prior chunks |

### Alternative Path (Low-Cost Mode)
Environment flag `LOW_COST_MODE=true` may:
- Skip layout model; use basic text extract
- Skip embeddings until first evaluation request
- Use larger chunk size to reduce tokenization overhead

### Chunking Heuristics (Draft)
| Parameter | Value (Initial) | Rationale |
|-----------|-----------------|-----------|
| Target tokens | 800 | Balance context richness vs. window occupancy |
| Min tokens | 200 | Avoid overly small fragments |
| Overlap tokens | 80 | Maintain continuity for cross-sentence references |
| Section boundary bias | Strong | Start new chunk at heading when possible |

### Index Update Modes
- Upsert per chunk (id = documentId + sequential suffix)
- Soft delete old chunks on re-ingest if content hash differs
- Store document-level metadata separately (Cosmos) to keep index lean

### Cosmos vs. Index Responsibilities
| Concern | Cosmos | Search Index |
|---------|--------|--------------|
| Status tracking | Yes | No |
| Full rule-independent metadata | Yes | Partial (selected fields) |
| Chunk text | No (optional backup) | Yes |
| Embeddings | In index vector field | Primary location |
| Audit trail | Yes | No |

### Security & Governance Notes
- SAS-scoped writes for upload client
- Private endpoint for Search + Cosmos (future hardening)
- Hash-based dedupe prevents storage bloat

### Metrics (Proposed)
- Ingestion latency (upload -> indexed)
- Extraction success rate (%)
- Avg tokens per chunk
- Re-ingest dedupe hit rate

### Minimal Pseudo Sequence
```
upload -> blob event -> queue message -> extractor worker ->
  call Document Intelligence -> poll until complete ->
  normalize -> chunk -> embed -> index ->
  write status (indexed) -> emit event (optional)
```

## Status Record Example
```jsonc
{
  "id": "rfp_2025_0042",
  "fileName": "RFP_CustomerPortal_v4.pdf",
  "blobPath": "rfps/2025/RFP_CustomerPortal_v4.pdf",
  "documentType": "RFP",
  "sizeBytes": 534221,
  "status": "indexed", // uploaded | extracting | indexing | indexed | error
  "chunkCount": 142,
  "hash": "sha256:...",
  "error": null,
  "lastUpdatedUtc": "2025-09-15T02:10:00Z"
}
```

## Index Field Draft
| Field | Type | Notes |
|-------|------|-------|
| id | string | chunk id |
| documentId | string | groups chunks |
| section | string | logical / inferred section |
| content | string | full text chunk |
| embedding | vector | semantic search |
| pageRange | string | source pages |
| metadata | string/json | dynamic properties |

## Considerations
- Idempotency via file hash
- Retry policies for extraction failures
- Max chunk token length boundaries
- Redaction layer (future)

## Open Questions
- Need inline table/image representation now or later?
- Should we enrich with key phrase extraction?

## Next Steps
- Define index schema JSON
- Prototype chunker heuristics
- Implement ingestion status service
