"""LLM Judge for evaluating agent performance."""

import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
from .config import Config

logger = logging.getLogger(__name__)


class LLMJudge:
    """LLM-based judge for evaluating agent outputs."""
    
    def __init__(self, model: Optional[str] = None, **kwargs):
        """Initialize the LLM judge.
        
        Args:
            model: Model name to use (defaults to config)
            **kwargs: Additional OpenAI client parameters
        """
        config = Config.get_judge_config()
        self.model = model or config["model"]
        self.temperature = config["temperature"]
        self.max_tokens = config["max_tokens"]
        
        # Initialize OpenAI client
        client_kwargs = {
            "api_key": config["api_key"],
            "base_url": config["base_url"],
            **kwargs
        }
        self.client = OpenAI(**{k: v for k, v in client_kwargs.items() if v is not None})
    
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

Your task:
1. Review the original document and evaluation criteria
2. Assess the agent's evaluation for accuracy, reasoning quality, and evidence relevance
3. Provide scores and detailed feedback for each criterion
4. Return your assessment as valid JSON

Scoring guidelines:
- 90-100: Excellent evaluation, accurate scoring, strong evidence, clear reasoning
- 80-89: Good evaluation, mostly accurate, adequate evidence and reasoning  
- 70-79: Fair evaluation, some inaccuracies, weak evidence or reasoning
- 60-69: Poor evaluation, significant inaccuracies, inadequate evidence
- 0-59: Very poor evaluation, major errors, irrelevant evidence

Be objective, thorough, and constructive in your feedback."""
    
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
        
        return f"""Please evaluate this AI agent's document evaluation:

{metadata_str}
Document Text:
---
{document_text[:3000]}{'...' if len(document_text) > 3000 else ''}
---

Evaluation Criteria:
{criteria_str}

Agent's Output:
---
{json.dumps(agent_output, indent=2)}
---

Please assess:
1. How accurately did the agent evaluate each criterion?
2. Is the agent's reasoning sound and well-supported?
3. Are the evidence snippets relevant and sufficient?
4. Are the scores appropriately calibrated?

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
      "judge_comments": "Detailed feedback...",
      "score_justification": "Why this score..."
    }}
  ],
  "judge_overall_comments": "Overall assessment..."
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
                    "judge_comments": "Not evaluated by judge",
                    "score_justification": "Missing from judge output"
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