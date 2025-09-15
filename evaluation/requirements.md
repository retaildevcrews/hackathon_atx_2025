# Agent Evaluation Requirements

## Dependencies

```bash
pip install openai requests pytest
```

## Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Azure OpenAI Configuration
export AZURE_OPENAI_API_KEY="your-azure-openai-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"
export AZURE_OPENAI_API_VERSION="2024-08-01-preview"
export JUDGE_MODEL="gpt-4"
export JUDGE_TEMPERATURE="0.1"

# Agent Configuration
export AGENT_ENDPOINT="http://localhost:8000/evaluate"
export AGENT_TIMEOUT="60"

# Evaluation Settings
export MIN_ACCEPTABLE_SCORE="70.0"
export CONSISTENCY_RUNS="3"
```

## Quick Start

1. **Install dependencies:**

   ```bash
   pip install openai requests pytest
   ```

2. **Set your Azure OpenAI credentials:**

   ```bash
   export AZURE_OPENAI_API_KEY="your-azure-openai-api-key"
   export AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"
   export AZURE_OPENAI_API_VERSION="2024-08-01-preview"
   ```

3. **Run the evaluation:**

   ```bash
   cd /workspaces/hackathon_atx_2025
   python -m evaluation.run_example
   ```

4. **Run tests:**

   ```bash
   python -m pytest evaluation/tests/ -v
   ```

## Usage Examples

### Basic Evaluation
```python
from evaluation import run_evaluation

results = run_evaluation(
    dataset_path="evaluation/dataset/test_cases.jsonl",
    agent_endpoint="http://localhost:8000/evaluate"
)

print(f"Mean score: {results['metrics']['summary']['mean_judge_score']}")
```

### Custom Judge Configuration
```python
from evaluation import Evaluator, LLMJudge

judge = LLMJudge(model="gpt-3.5-turbo", temperature=0.2)
evaluator = Evaluator(judge=judge)

results = evaluator.run_evaluation(
    dataset_path="my_dataset.jsonl",
    consistency_runs=5
)
```

### Analysis Only (Mock Agent)
```python
# For testing the judge without calling the real agent
from evaluation.tests.test_evaluation import TestIntegration
test = TestIntegration()
test.test_full_evaluation_pipeline()
```

## Dataset Format

Each line in the JSONL dataset should contain:
```json
{
  "document_id": "unique_id",
  "document_text": "Full document content...",
  "document_metadata": {
    "title": "Document Title",
    "source": "system_name",
    "date": "2025-09-15"
  },
  "criteria": [
    {
      "criterion_id": "criterion_name",
      "description": "What to evaluate",
      "weight": 1.0
    }
  ]
}
```

## Agent API Contract

Your agent must expose a POST endpoint that accepts:
```json
{
  "document_text": "string",
  "criteria": [{"criterion_id": "string", "description": "string", "weight": 1.0}],
  "document_metadata": {}
}
```

**Important**: The agent will receive the full document_text in the API call, but internally should use a retrieval tool to extract only relevant chunks for evaluation.

And returns:
```json
{
  "document_id": "string",
  "overall_score": 85.0,
  "criteria_evaluations": [
    {
      "criterion_id": "string",
      "score": 85.0,
      "confidence": 0.8,
      "reasoning": "Detailed explanation based on retrieved chunks...",
      "supporting_evidence": [
        {"text": "Evidence snippet", "chunk_id": "chunk_003", "relevance_score": 0.92}
      ],
      "pass": true,
      "chunks_used": ["chunk_001", "chunk_003"]
    }
  ],
  "input_chunks": [
    {
      "chunk_id": "chunk_001",
      "text": "Retrieved chunk content that was fed to evaluation logic...",
      "relevance_score": 0.92,
      "used_in_criteria": ["security_compliance"]
    }
  ],
  "retrieval_summary": {
    "total_chunks_retrieved": 8,
    "chunks_used_in_evaluation": 5,
    "retrieval_quality_estimate": 0.87
  }
}
```

## Interpreting Results

### Metrics
- **Mean Judge Score**: Average quality rating (0-100)
- **Score Distribution**: Performance breakdown by ranges
- **Agent vs Judge Correlation**: How well agent scores align with judge scores
- **Per-Criterion Performance**: Breakdown by evaluation criteria

### Score Ranges
- **90-100**: Excellent evaluation
- **80-89**: Good evaluation
- **70-79**: Fair evaluation (meets minimum threshold)
- **60-69**: Poor evaluation
- **0-59**: Very poor evaluation

### Common Issues

- **Inadequate Chunk Retrieval**: Retrieval tool didn't fetch relevant chunks for criteria
- **Poor Chunk Utilization**: Agent didn't effectively use the retrieved chunks
- **Missing Evidence**: Agent didn't provide sufficient supporting evidence from chunks
- **Over-scoring**: Agent scores too optimistically vs judge assessment
- **Weak Reasoning**: Agent explanations lack depth or don't follow from chunk content
- **Chunk Misinterpretation**: Agent incorrectly interpreted or cited chunk content
