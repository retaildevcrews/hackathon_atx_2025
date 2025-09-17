# GitHub Issue: Agent Document Evaluation Endpoint

## Title

Add rubric-based PDF evaluation endpoint to Agent service

## Summary

Implement a new endpoint that accepts (stubbed) a document reference, evaluates a PDF against each criterion in a rubric using an LLM (one call per criterion), and returns aggregated structured scoring output.

## Motivation

Enables automated, explainable scoring of product documents against standardized rubric criteria to support downstream decision workflows and reporting. Establishes a foundation for later retrieval, chunking, and persistence enhancements.

## Acceptance criteria

- POST endpoint (path: `/evaluate_rubric`) returns 200 with aggregated results when model succeeds for all criteria
- Reads rubric JSON (`apps/agent/sample_data/tv_rubric.json`)
- Uses rubric name as `rubric_id`; criterion id = slug(name)
- One LLM invocation per criterion (no batching)
- Concurrency controlled by semaphore; default max 5; overridable per request (`max_concurrency`)
- Sends full, un-chunked PDF bytes (local sample PDF) as multimodal input to model
- System prompt template included verbatim in response under `system_prompt_template`
- Each criterion result fields: `criterion_id`, `criterion_name`, `criterion_description`, `criterion_definition` (object), `weight`, `score` (int 1–5), `reasoning`, `evidence` (single string), `document_chunk` (null / placeholder because no chunking yet)
- Response top-level includes: `rubric_id`, `rubric_name`, `criteria` (list), `model_params` (effective params), `system_prompt_template`
- Logs raw model responses AND parsed structures (PII allowed)
- On any single criterion model failure (API/network), entire request returns 500 (no partial success)
- If model returns malformed JSON, malformed text placed directly into `reasoning`, `score` = null, still treated as success for that criterion (overall 200)
- No retries; no JSON repair beyond direct parse attempt
- Evidence returned as single string (if model returns list, join with space)

## Scope

Included:

- New FastAPI route & request/response models
- Rubric loader + simple slug utility
- Evaluation service with concurrency control
- System prompt template definition
- Logging integration (raw + parsed)

Excluded (future work):

- Azure Blob fetch (stub uses local file path only)
- Document chunking / retrieval
- Embeddings / semantic relevance filtering
- Persistence of evaluation results
- Retry / resiliency strategies
- Streaming responses
- GUID-based rubric / criterion IDs

## Out of scope

- Partial success handling
- Automatic JSON schema repair
- Token length safeguards / truncation
- Security redaction of logs

## Design overview

Flow:

1. Load rubric JSON once (cache in memory) providing rubric + criteria metadata.
2. Receive POST request with optional `document_url`, optional `model_params`, optional `max_concurrency`.
3. Load local sample PDF file (`apps/agent/sample_data/LG_SPEC-SHEET_UM670H_Series_122327_LR[20240131_040303].pdf`) and read bytes.
Steps detail:

- For each criterion (order preserved or arbitrary—no requirement):
  - Build prompt: system template (placeholders kept), user content includes criterion metadata + flattened scoring definition + note instructing single-string evidence.
  - Attach PDF bytes per LangChain / OpenAI multimodal usage pattern.
  - Invoke model with temperature=0 (unless overridden via `model_params`).
  - Attempt JSON parse; if success, extract fields; if failure, set `score=null`, `reasoning=raw_response`, `evidence=""`.
- Assemble results and return aggregated response.
- Log full raw + parsed outputs.
- Expose effective `model_params` (merged defaults + overrides) in response.

Concurrency:

- Use `asyncio.Semaphore(max_concurrency)` to bound simultaneous LLM calls.

Error handling:

- Transport / API errors cause immediate 500 abort (abort remaining tasks via cancellation).
- Malformed JSON does not cause 500; criterion treated as degraded success.

IDs:

- `rubric_id = rubric_name` from JSON.
- `criterion_id = slug(criterion_name)` (lowercase, hyphen, alphanumeric only).

System prompt template (stored constant):

```text
You are an expert document evaluator. Evaluate the following document content against the given criterion.

Instructions:
- Provide a score strictly following the scale and rules defined in the Scoring Criteria.
- Explain the reasoning in detail, including why the score was chosen.
- Extract specific evidence from the document to support the reasoning. Evidence must be a single concise quote or paraphrased excerpt string (not a list).
- If no relevant evidence exists, use an empty string for evidence and explain why in reasoning.
- Output must be valid JSON only, with no extra text.
```

## Request schema (proposed)

```json
{
  "document_url": "string (optional, ignored for now)",
  "rubric_name": "string (optional, default tv_rubric)",
  "model_params": {"temperature": 0},
  "max_concurrency": 5
}
```

## Response schema (example)

```json
{
  "rubric_id": "tv_rubric",
  "rubric_name": "tv_rubric",
  "criteria": [
    {
      "criterion_id": "picture-quality",
      "criterion_name": "Picture Quality",
      "criterion_description": "Measures resolution, contrast, color accuracy, and HDR support.",
      "criterion_definition": {
        "Excellent (5)": "OLED/QLED, 4K/8K, HDR10+, Dolby Vision",
        "Good (4)": "High-res LED, good contrast",
        "Fair (3)": "Standard HD, decent colors",
        "Poor (2)": "Washed out or uneven",
        "Very Poor (1)": "Blurry or pixelated"
      },
      "weight": "20%",
      "score": 5,
      "reasoning": "Model provided rationale...",
      "evidence": "\"OLED panel with HDR10+ support\"",
      "document_chunk": null
    }
  ],
  "model_params": {"temperature": 0},
  "system_prompt_template": "You are an expert document evaluator..."
}
```

## Impacted code

- `apps/agent/routes/` (new `evaluate.py`)
- `apps/agent/services/` (new `evaluation_service.py`)
- `apps/agent/main.py` (include router)
- `apps/agent/config.py` (ensure env var for model deployment + concurrency default)
- `apps/agent/sample_data/tv_rubric.json` (read only)

## Test plan

- 200 success with all criteria producing integer scores
- Criterion malformed JSON still yields 200 and null score
- Overriding `max_concurrency` reduces simultaneous tasks (instrument with small artificial delay in tests if needed)
- 500 when mock model call raises exception
- Evidence single string (never list) in final output
- Slug generation deterministic and lowercase

## Risks and mitigations

- Large PDFs may exceed model context → deferred chunking; document for now
- Malformed outputs reduce utility → future enhancement: schema-enforced tool or response format validator
- Performance with many criteria → concurrency control
- Logging PII → future config flag to redact

## Definition of Done

- Endpoint implemented and integrated
- Example request/response added to agent README
- Logging present for raw & parsed outputs
- Basic tests (unit or integration) for success and error paths

## Follow-ups (not in this issue)

- Azure Blob fetch integration
- Chunking & retrieval augmentation
- Embeddings + relevance ranking
- Persistent storage of evaluations
- Retry & JSON schema enforcement
- Streaming partial responses
- GUID-based IDs from storage metadata
