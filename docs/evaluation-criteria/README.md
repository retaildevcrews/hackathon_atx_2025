# Evaluation Criteria Authoring & Rule Store

> **Status:** Early prototype – core CRUD and retrieval patterns are being shaped; publishing workflow and validation linting are future.

## Purpose

Provide a way to define, version, and retrieve rule templates ("rubrics") used to evaluate documents and other inputs. The `criteria_api` service owns persistence (Cosmos DB) and exposes retrieval endpoints consumed by the evaluation agent.

## Core Concerns (Phase 1 vs Future)

| Concern | Phase 1 (Prototype) | Future |
|---------|---------------------|--------|
| Template schema | Minimal fields (id, criteria, weights) | Rich metadata, localization |
| Versioning | Manual (new id) | Immutable published versions + draft channel |
| Immutability | Not enforced yet | Enforced after publish flag |
| Partitioning | Single container / simple partition key | Multi-tenant / logical partitioning |
| Validation | Basic shape checks | Semantic lint (weight sum, duplicates, reserved ids) |
| CRUD API | Create/read/delete (TBD) | Draft/publish lifecycle + audit trail |

## Draft Schema (Current Direction)

```jsonc
{
  "id": "rfp_security_pack_v1",
  "documentType": "RFP",
  "version": "1.0.0",
  "dimensions": ["security", "completeness", "alignment"],
  "rules": [
    {
      "id": "rfp_security_encryption",
      "category": "security",
      "check": "presence",
      "targetSection": ["Security", "Data Protection"],
      "requireKeywords": ["encryption", "AES", "TLS"],
      "weight": 0.15,
      "severity": "high",
      "remediationHint": "Specify algorithms and key rotation."
    }
  ],
  "scoring": { "aggregation": "weighted_sum" },
  "createdUtc": "2025-09-15T00:00:00Z",
  "createdBy": "user@org"
}
```

## APIs (Proposed / Iterating)

- GET /rules/{documentType}/{version}
- GET /rules/{documentType}/latest
- POST /rules (creates draft)
- POST /rules/{id}/publish
- DELETE /rules/{id} (soft delete / optional)

## Open Questions

- Should we allow rule referencing other rule outputs?
- Do we need tagging (e.g., domain=finance)?
- Multi-language support for rule text?

## Next Steps

- Implement initial POST/GET in `criteria_api`
- Add weight sum validator (1.0 ± epsilon)
- Introduce `status: draft|published`
- Seed with a minimal RFP + generic evaluation example
