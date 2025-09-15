# Evaluation Criteria Authoring & Rule Store

## Purpose

Provide a way to define, version, and retrieve rule templates used to evaluate documents.

## Core Concerns

- Template schema (rules, weights, dimensions)
- Versioning & immutability
- Cosmos DB data model & partitioning
- API surface for CRUD + publish
- Validation & linting of rule definitions

## Draft Schema

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

## APIs (Proposed)

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

- Finalize schema
- Implement validation logic
- Seed with a minimal RFP template
