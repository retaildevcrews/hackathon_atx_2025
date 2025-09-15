# Agent Evaluation Framework

This folder contains the evaluation framework for assessing how well our document evaluation agent performs.

## Approach

Since we don't have ground truth labels, we use an **LLM Judge** approach:

1. **Agent** receives document and criteria → uses retrieval tool to get relevant chunks → evaluates criteria based on chunks → produces JSON output
2. **LLM Judge** reviews the agent's chunk-based evaluation against the original document and criteria → scores the agent's performance
3. **Metrics** aggregate judge scores to track agent quality over time

**Key Insight**: The agent only receives relevant chunks (not the full document), so the judge evaluates both the agent's reasoning quality AND whether the retrieval tool provided adequate chunks.

## Structure

```text
evaluation/
├── README.md                 # This file
├── schema.md                 # Dataset and output schemas
├── evaluator.py             # Main evaluation orchestrator
├── llm_judge.py             # LLM judge implementation (chunk-aware)
├── metrics.py               # Scoring and reporting functions
├── utils.py                 # Helper functions
├── dataset/                 # Test documents and criteria
│   └── test_cases.jsonl     # Test dataset
├── reports/                 # Evaluation reports
├── tests/                   # Unit tests
└── config.py                # Configuration (model settings, etc.)
```

## Usage

```python
from evaluation.evaluator import run_evaluation
from evaluation.llm_judge import LLMJudge

# Run evaluation on test dataset
results = run_evaluation(
    dataset_path="evaluation/dataset/test_cases.jsonl",
    agent_endpoint="http://localhost:8000/evaluate",
    judge=LLMJudge(model="gpt-4")
)

# Generate report
results.save_report("evaluation/reports/")
```

## Metrics

- **Judge Score**: Average score the LLM judge gives the agent (0-100)
- **Chunk Utilization**: How effectively the agent used retrieved chunks
- **Retrieval Assessment**: Quality of chunks provided by retrieval tool
- **Reasoning Quality**: How well agent reasoned from available chunk information
- **Coverage**: Whether agent addresses all criteria given available chunks
