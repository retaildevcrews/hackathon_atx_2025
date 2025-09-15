# Evaluation Schemas

## Test Dataset Schema

Each test case contains a document and criteria to evaluate. No ground truth labels needed.

```json
{
  "document_id": "doc_001",
  "document_text": "Full text of the document to be evaluated...",
  "document_metadata": {
    "title": "Document Title",
    "source": "source_system",
    "date": "2025-09-15"
  },
  "criteria": [
    {
      "criterion_id": "security_compliance",
      "description": "Document must demonstrate security compliance measures",
      "weight": 1.0
    },
    {
      "criterion_id": "completeness",
      "description": "All required sections must be present and complete",
      "weight": 1.0
    }
  ]
}
```

## Agent Output Schema

Expected JSON output from the evaluation agent:

```json
{
  "document_id": "doc_001",
  "evaluation_timestamp": "2025-09-15T10:30:00Z",
  "overall_score": 85.0,
  "criteria_evaluations": [
    {
      "criterion_id": "security_compliance",
      "score": 90.0,
      "confidence": 0.85,
      "reasoning": "Document includes comprehensive security protocols...",
      "supporting_evidence": [
        {
          "text": "Security protocols are implemented...",
          "relevance_score": 0.92
        }
      ],
      "pass": true
    }
  ]
}
```

## Judge Output Schema

LLM Judge evaluation of agent performance:

```json
{
  "judge_id": "gpt-4-2024-09-15",
  "evaluation_timestamp": "2025-09-15T10:35:00Z",
  "document_id": "doc_001",
  "overall_judge_score": 78.0,
  "criteria_judgments": [
    {
      "criterion_id": "security_compliance",
      "agent_score": 90.0,
      "judge_score": 85.0,
      "accuracy": "high",
      "reasoning_quality": "good",
      "evidence_relevance": "high",
      "judge_comments": "Agent correctly identified security measures but could have better synthesized information...",
      "score_justification": "Agent's score of 90 is slightly optimistic; 85 more appropriate given analysis depth"
    }
  ],
  "judge_overall_comments": "Agent performed well with good reasoning and appropriate scoring..."
}
```

## Metrics Schema

Aggregated evaluation results:

```json
{
  "evaluation_run_id": "eval_2025_09_15_001",
  "timestamp": "2025-09-15T11:00:00Z",
  "dataset_size": 25,
  "summary": {
    "mean_judge_score": 76.4,
    "median_judge_score": 78.0,
    "std_judge_score": 12.3,
    "agent_vs_judge_correlation": 0.82
  },
  "per_criterion": {
    "security_compliance": {
      "mean_judge_score": 78.2,
      "agreement_rate": 0.84,
      "common_issues": ["Missing edge cases", "Over-optimistic scoring"]
    }
  },
  "recommendations": [
    "Improve evidence selection for security criteria",
    "Calibrate confidence scores"
  ]
}
```
