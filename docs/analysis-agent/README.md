# Analysis Agent & Structured Evaluation

## Purpose
Combine deterministic rule checks with LLM reasoning to produce structured evaluation output.

## High-Level Sequence
1. Request: { documentId, ruleTemplateId }
2. Fetch rule template from Cosmos.
3. For each rule/dimension: retrieve relevant chunks (semantic + keyword filter).
4. Apply deterministic checks (presence, keyword coverage, pattern match).
5. Build prompt with context + rule spec for LLM reasoning where needed.
6. Parse LLM output (JSON mode or schema-guided) for rationale and inferred attributes.
7. Aggregate scores -> dimension -> overall.
8. Persist evaluation record.

## Output Contract (Draft)
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

## Error Handling
- Partial failure isolation (continue other rules)
- Mark failed rules with status=error and reason
- Retry limited to transient retrieval / LLM timeouts

## Open Questions
- Streaming intermediate findings to UI?
- Should rules express dependency graph?
- Adaptive prompt size strategies?

## Next Steps
- Define deterministic rule evaluator interface
- Draft prompt templates per rule type
- Implement evaluation aggregator prototype
