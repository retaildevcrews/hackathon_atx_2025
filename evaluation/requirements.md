# Agent Evaluation Requirements

## Dependencies

```bash
pip install openai requests pytest
```

## Environment Variables

Create a `.env` file or set these environment variables:

```bash
# LLM Judge Configuration
export JUDGE_MODEL="gpt-4"
export OPENAI_API_KEY="your-openai-api-key"
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

2. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
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
      "reasoning": "Detailed explanation...",
      "supporting_evidence": [
        {"text": "Evidence snippet", "start_char": 100, "end_char": 200}
      ],
      "pass": true
    }
  ]
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
- **Missing Evidence**: Agent didn't provide sufficient supporting evidence
- **Over-scoring**: Agent scores too optimistically vs judge assessment
- **Weak Reasoning**: Agent explanations lack depth or accuracy
- **Irrelevant Evidence**: Agent cited evidence not relevant to criteria