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

Expected JSON output from the evaluation agent (note: agent only receives relevant chunks, not full document):

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
      "reasoning": "Based on retrieved chunks, document includes comprehensive security protocols...",
      "supporting_evidence": [
        {
          "text": "Security protocols are implemented...",
          "chunk_id": "chunk_003",
          "relevance_score": 0.92
        }
      ],
      "pass": true,
      "chunks_used": ["chunk_001", "chunk_003", "chunk_007"]
    }
  ],
  "retrieval_summary": {
    "total_chunks_retrieved": 8,
    "chunks_used_in_evaluation": 5,
    "retrieval_quality_estimate": 0.87
  },
  "input_chunks": [
    {
      "chunk_id": "chunk_001",
      "text": "Relevant document section that was fed to agent...",
      "relevance_score": 0.92,
      "used_in_criteria": ["security_compliance", "data_protection"]
    }
  ]
}
```

## Judge Output Schema

LLM Judge evaluation of agent performance (evaluating chunk-based reasoning):

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
      "chunk_utilization": "effective",
      "retrieval_adequacy": "sufficient",
      "judge_comments": "Agent correctly identified security measures from retrieved chunks but could have better synthesized information across chunks...",
      "score_justification": "Agent's score of 90 is slightly optimistic; 85 more appropriate given incomplete chunk coverage",
      "missing_information": "Agent missed some security details that appear in non-retrieved chunks"
    }
  ],
  "retrieval_assessment": {
    "chunk_relevance": "high",
    "chunk_coverage": "adequate",
    "missing_critical_info": false,
    "retrieval_quality_score": 82.0
  },
  "judge_overall_comments": "Agent performed well with available chunks but evaluation limited by retrieval scope..."
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
