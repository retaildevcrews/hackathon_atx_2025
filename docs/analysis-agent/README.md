# Analysis Agent & Structured Evaluation

> **Status:** Prototype – core orchestration logic is emerging inside `apps/agent` using Azure OpenAI. Retrieval + deterministic rule blending is partially stubbed; full ingestion + search integration pending.

## Purpose

Combine deterministic rule checks with LLM reasoning to produce structured evaluation output.

## High-Level Sequence (Current vs. Target)

1. (Current) Request: { ruleTemplateId, payload? } – document retrieval mocked / simplified
2. Load rule template via `criteria_api` (HTTP GET)
3. (Future) Retrieve relevant indexed chunks (semantic + keyword filters)
4. Run deterministic presence / keyword checks
5. Build prompt(s) with structured rule context for Azure OpenAI
6. Parse model response (JSON mode / schema) to extract rationale + status
7. Aggregate rule scores -> dimension -> overall composite
8. Persist evaluation record (planned store)

## Output Contract (Draft – Subject to Change)

```jsonc
{
  "id": "eval_rfp_2025_0042_v1",
  "documentId": "rfp_2025_0042",
  "ruleTemplateId": "rfp_security_pack_v1",
  "overallScore": 0.82,
  "dimensionScores": { "security": 0.74, "completeness": 0.88, "alignment": 0.90 },
  "findings": [
    {
      "ruleId": "rfp_security_encryption",
      "status": "partial", // pass | fail | partial | missing
      "score": 0.6,
      "missing": ["key rotation policy"],
      "rationale": "Encryption mentioned but lacks lifecycle details.",
      "recommendation": "Add rotation interval and certificate management process.",
      "evidenceChunkIds": ["rfp_2025_0042_c087", "rfp_2025_0042_c094"]
    }
  ],
  "timingMs": { "retrieval": 340, "llm": 1820, "aggregation": 25 },
  "createdUtc": "2025-09-15T03:05:00Z"
}
```

## Tooling (Potential MCP Tools)

- retrieval.search
- rules.loadTemplate
- rules.evaluateDeterministic
- llm.reason
- scoring.aggregate
- evaluations.persist

## Error Handling (Planned)

- Partial failure isolation (continue other rules)
- Mark failed rules with status=error and reason
- Retry limited to transient retrieval / LLM timeouts

## Open Questions

- Streaming intermediate findings to UI?
- Should rules express dependency graph?
- Adaptive prompt size strategies?

## Environment Variables

The agent relies on the following (see `apps/agent/.env.example`):

| Variable | Purpose |
|----------|---------|
| AZURE_OPENAI_API_KEY | Auth for Azure OpenAI completion / chat / embeddings |
| AZURE_OPENAI_ENDPOINT | Base endpoint for Azure OpenAI resource |
| AZURE_OPENAI_DEPLOYMENT | Model deployment name used for reasoning calls |
| AZURE_OPENAI_API_VERSION | API version (pinned for consistency) |
| AZURE_SEARCH_ENDPOINT | (Future) Cognitive Search endpoint for retrieval |
| AZURE_SEARCH_API_KEY | (Future) API key for search queries |
| AZURE_SEARCH_INDEX | (Future) Index name containing chunks |
| CRITERIA_API_URL | Base URL to fetch rule templates |
| LOG_LEVEL | Adjust logging verbosity |

## Next Steps

- Introduce retrieval abstraction (noop adapter initially)
- Add deterministic evaluator module (keyword / presence)
- Implement prompt templating with guardrails (length, schema enforcement)
- Persist evaluation results (Cosmos or file-based prototype)
- Add lightweight cost / timing metrics collection
