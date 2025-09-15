"""LLM Judge for evaluating agent performance."""

import json
import logging
from typing import Dict, List, Any, Optional
from openai import AzureOpenAI
from .config import Config

logger = logging.getLogger(__name__)


class LLMJudge:
    """LLM-based judge for evaluating agent outputs."""

    def __init__(self, model: Optional[str] = None, **kwargs):
        """Initialize the LLM judge.

        Args:
            model: Model name to use (defaults to config)
            **kwargs: Additional Azure OpenAI client parameters
        """
        config = Config.get_judge_config()
        self.model = model or config["model"]
        self.temperature = config["temperature"]
        self.max_tokens = config["max_tokens"]

        # Initialize Azure OpenAI client
        client_kwargs = {
            "api_key": config["api_key"],
            "azure_endpoint": config["azure_endpoint"],
            "api_version": config["api_version"],
            **kwargs
        }
        self.client = AzureOpenAI(**{k: v for k, v in client_kwargs.items() if v is not None})

    def evaluate_agent_output(
        self,
        document_text: str,
        criteria: List[Dict[str, Any]],
        agent_output: Dict[str, Any],
        document_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate an agent's output against the original document and criteria.

        Args:
            document_text: The original document text
            criteria: List of evaluation criteria
            agent_output: The agent's evaluation output
            document_metadata: Optional document metadata

        Returns:
            Judge evaluation with scores and feedback
        """
        try:
            # Build the judge prompt
            prompt = self._build_judge_prompt(
                document_text, criteria, agent_output, document_metadata
            )

            # Get judge response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )

            # Parse and validate response
            judge_output = json.loads(response.choices[0].message.content)
            return self._validate_judge_output(judge_output, criteria, agent_output)

        except Exception as e:
            logger.error(f"Error in judge evaluation: {e}")
            return self._create_error_response(str(e), agent_output)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM judge."""
        return """You are an expert evaluator assessing how well an AI agent evaluated a document against specific criteria.

IMPORTANT: The agent only receives RELEVANT CHUNKS from the document (via a retrieval tool), NOT the full document. Your evaluation should account for this limitation.

Your task:
1. Review the original document, evaluation criteria, and chunks the agent received
2. Assess whether the agent made good use of the available chunks
3. Evaluate the agent's reasoning quality given the information it had access to
4. Consider whether the retrieval tool provided adequate chunks for evaluation
5. Provide scores and detailed feedback for each criterion

Key evaluation dimensions:
- **Accuracy**: How well did the agent evaluate criteria based on available chunks?
- **Reasoning Quality**: Is the agent's reasoning sound given the chunk information?
- **Chunk Utilization**: Did the agent effectively use the retrieved chunks?
- **Evidence Relevance**: Are cited evidence snippets appropriate and well-selected?
- **Retrieval Adequacy**: Were the retrieved chunks sufficient for proper evaluation?

Scoring guidelines:
- 90-100: Excellent evaluation, optimal use of chunks, strong reasoning, accurate scoring
- 80-89: Good evaluation, effective chunk usage, mostly accurate reasoning
- 70-79: Fair evaluation, adequate chunk usage, some reasoning gaps
- 60-69: Poor evaluation, ineffective chunk usage, significant reasoning issues
- 0-59: Very poor evaluation, major errors in chunk interpretation

Be objective and consider that the agent's limitations may stem from inadequate chunk retrieval rather than poor reasoning."""

    def _build_judge_prompt(
        self,
        document_text: str,
        criteria: List[Dict[str, Any]],
        agent_output: Dict[str, Any],
        document_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the evaluation prompt for the judge."""
        metadata_str = ""
        if document_metadata:
            metadata_str = f"\nDocument Metadata:\n{json.dumps(document_metadata, indent=2)}\n"

        criteria_str = "\n".join([
            f"- {c['criterion_id']}: {c['description']} (weight: {c.get('weight', 1.0)})"
            for c in criteria
        ])

        # Extract chunks that were fed to the agent
        input_chunks = agent_output.get("input_chunks", [])
        chunks_str = ""
        if input_chunks:
            chunks_str = "\n\nChunks Retrieved for Agent:\n---\n"
            for i, chunk in enumerate(input_chunks[:5]):  # Limit to first 5 chunks
                chunk_text = chunk.get("text", "")[:500]  # Truncate long chunks
                relevance = chunk.get("relevance_score", "unknown")
                chunks_str += f"Chunk {i+1} (relevance: {relevance}):\n{chunk_text}\n\n"
            if len(input_chunks) > 5:
                chunks_str += f"... and {len(input_chunks) - 5} more chunks\n"
            chunks_str += "---\n"

        return f"""Please evaluate this AI agent's document evaluation based on chunks it received:

{metadata_str}
Original Document (for your reference - agent did NOT see this full text):
---
{document_text[:2000]}{'...' if len(document_text) > 2000 else ''}
---

Evaluation Criteria:
{criteria_str}
{chunks_str}
Agent's Output (based only on chunks above):
---
{json.dumps(agent_output, indent=2)}
---

CRITICAL: The agent only had access to the retrieved chunks shown above, NOT the full document.

Please assess:
1. How well did the agent evaluate each criterion given the available chunks?
2. Is the agent's reasoning sound based on the chunk information it had?
3. Did the agent effectively utilize the retrieved chunks?
4. Are the evidence snippets relevant and properly cited from the chunks?
5. Were the retrieved chunks sufficient for proper evaluation? (This affects the agent's ability to perform)

Return your evaluation as JSON with this structure:
{{
  "judge_id": "{self.model}",
  "evaluation_timestamp": "2025-09-15T10:35:00Z",
  "document_id": "{agent_output.get('document_id', 'unknown')}",
  "overall_judge_score": 85.0,
  "criteria_judgments": [
    {{
      "criterion_id": "criterion_name",
      "agent_score": 90.0,
      "judge_score": 85.0,
      "accuracy": "high|medium|low",
      "reasoning_quality": "excellent|good|fair|poor",
      "evidence_relevance": "high|medium|low",
      "chunk_utilization": "excellent|good|fair|poor",
      "retrieval_adequacy": "sufficient|partial|insufficient",
      "judge_comments": "Detailed feedback on agent's chunk-based evaluation...",
      "score_justification": "Why this score given available chunks...",
      "missing_information": "What critical info was missing from chunks (if any)..."
    }}
  ],
  "retrieval_assessment": {{
    "chunk_relevance": "high|medium|low",
    "chunk_coverage": "comprehensive|adequate|limited",
    "missing_critical_info": true|false,
    "retrieval_quality_score": 85.0
  }},
  "judge_overall_comments": "Overall assessment considering chunk limitations..."
}}"""

    def _validate_judge_output(
        self,
        judge_output: Dict[str, Any],
        criteria: List[Dict[str, Any]],
        agent_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and normalize judge output."""
        # Ensure required fields exist
        required_fields = ["overall_judge_score", "criteria_judgments"]
        for field in required_fields:
            if field not in judge_output:
                logger.warning(f"Missing required field: {field}")
                judge_output[field] = 0.0 if field == "overall_judge_score" else []

        # Validate criteria judgments
        if not isinstance(judge_output["criteria_judgments"], list):
            judge_output["criteria_judgments"] = []

        # Ensure all criteria are covered
        criteria_ids = {c["criterion_id"] for c in criteria}
        judged_ids = {j.get("criterion_id") for j in judge_output["criteria_judgments"]}

        missing_criteria = criteria_ids - judged_ids
        if missing_criteria:
            logger.warning(f"Judge missed criteria: {missing_criteria}")
            # Add placeholder judgments for missing criteria
            for criterion_id in missing_criteria:
                judge_output["criteria_judgments"].append({
                    "criterion_id": criterion_id,
                    "agent_score": 0.0,
                    "judge_score": 0.0,
                    "accuracy": "unknown",
                    "reasoning_quality": "unknown",
                    "evidence_relevance": "unknown",
                    "chunk_utilization": "unknown",
                    "retrieval_adequacy": "unknown",
                    "judge_comments": "Not evaluated by judge",
                    "score_justification": "Missing from judge output",
                    "missing_information": "N/A"
                })

        return judge_output

    def _create_error_response(self, error_msg: str, agent_output: Dict[str, Any]) -> Dict[str, Any]:
        """Create an error response when judge evaluation fails."""
        return {
            "judge_id": self.model,
            "evaluation_timestamp": "2025-09-15T00:00:00Z",
            "document_id": agent_output.get("document_id", "unknown"),
            "overall_judge_score": 0.0,
            "criteria_judgments": [],
            "judge_overall_comments": f"Judge evaluation failed: {error_msg}",
            "error": True
        }
