"""
LangChain-based evaluation service for document assessment against rubrics.
Uses criteria_api service for rubric and criteria data.
"""

import logging
from typing import Any, Dict, List, Optional
from functools import lru_cache

from models.invoke import CriterionEvaluation, EvaluationResult
from services.criteria_bridge import CriteriaAPIBridge, get_criteria_api_bridge
from services.search_service import AzureSearchService
from prompts.evaluation_prompts import get_batch_evaluation_template, get_summary_template
from config import get_settings

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for evaluating documents using LangChain/LangGraph."""

    def __init__(
        self,
        criteria_bridge: CriteriaAPIBridge,
        search_service: AzureSearchService,
        llm: Optional[Any] = None
    ):
        """Initialize evaluation service.

        Args:
            criteria_bridge: Bridge service for criteria_api integration
            search_service: Azure Search service for document chunks
            llm: LangChain LLM instance (will create if None)
        """
        self.criteria_bridge = criteria_bridge
        self.search_service = search_service
        self.settings = get_settings()

        # Initialize LLM if not provided
        if llm is None:
            self.llm = self._create_llm()
        else:
            self.llm = llm

        # Get prompt templates
        self.batch_evaluation_template = get_batch_evaluation_template()
        self.summary_template = get_summary_template()

    def _create_llm(self) -> Any:
        """Create LangChain LLM instance."""
        try:
            # Import here to avoid dependency issues if LangChain not installed
            from langchain_openai import AzureChatOpenAI

            if not all([
                self.settings.azure_openai_api_key,
                self.settings.azure_openai_endpoint,
                self.settings.azure_openai_deployment
            ]):
                logger.warning("Azure OpenAI not fully configured; using stub LLM")
                return None

            return AzureChatOpenAI(
                azure_deployment=self.settings.azure_openai_deployment,
                api_key=self.settings.azure_openai_api_key,
                azure_endpoint=self.settings.azure_openai_endpoint,
                api_version=self.settings.azure_openai_api_version,
                temperature=0.1,
                timeout=120
            )
        except ImportError:
            logger.warning("LangChain not available; using stub LLM")
            return None

    async def evaluate_document(
        self,
        document_text: str,
        rubric_name: str,
        document_id: Optional[str] = None,
        max_chunks: int = 10
    ) -> Dict[str, Any]:
        """Evaluate a document against a rubric.

        Args:
            document_text: Text content to evaluate
            rubric_name: Name of rubric to use
            document_id: Optional document ID for search filtering
            max_chunks: Maximum chunks to retrieve per criterion

        Returns:
            Evaluation results dictionary
        """
        try:
            # Step 1: Load rubric from criteria_api
            rubric_data = await self.criteria_bridge.get_rubric(rubric_name)
            if not rubric_data:
                return {
                    "error": f"Rubric '{rubric_name}' not found",
                    "overall_score": 0.0,
                    "criteria_evaluations": [],
                    "summary": f"Evaluation failed: Rubric '{rubric_name}' not found"
                }

            # Step 2: Retrieve document chunks
            document_chunks = await self._retrieve_chunks(
                document_text, rubric_data, document_id, max_chunks
            )

            # Step 3: Evaluate all criteria at once
            criteria_evaluations = await self._evaluate_criteria_batch(
                rubric_data, document_chunks
            )

            # Step 4: Create summary
            summary_data = await self._create_summary(
                rubric_name, criteria_evaluations
            )

            # Step 5: Calculate overall score
            overall_score = self._calculate_overall_score(criteria_evaluations)

            # Build result
            result = EvaluationResult(
                overall_score=overall_score,
                document_id=document_id,
                rubric_name=rubric_name,
                criteria_evaluations=criteria_evaluations,
                summary=summary_data["summary"],
                strengths=summary_data["strengths"],
                improvements=summary_data["improvements"],
                agent_metadata={
                    "evaluation_model": "langchain-azure-openai",
                    "chunks_analyzed": str(len(document_chunks)),  # Convert to string
                    "workflow": "batch_evaluation"
                }
            )

            return result.dict()

        except Exception as e:
            logger.error(f"Error during document evaluation: {e}")
            return {
                "error": str(e),
                "overall_score": 0.0,
                "criteria_evaluations": [],
                "summary": f"Evaluation failed: {e}"
            }

    async def _retrieve_chunks(
        self,
        document_text: str,
        rubric_data: Dict[str, Any],
        document_id: Optional[str],
        max_chunks: int
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant document chunks."""
        chunks = []

        if self.search_service.enabled:
            # Search for chunks relevant to each criterion
            for criterion in rubric_data["criteria"]:
                query = f"{criterion['criterion_id']} {criterion['description']}"
                search_results = await self.search_service.search(query, top=3)

                for result in search_results:
                    chunk = {
                        "chunk_id": result.get("id", "unknown"),
                        "document_id": document_id,
                        "content": result.get("content", ""),
                        "related_criterion": criterion["criterion_id"],
                        "score": result.get("score", 0.0)
                    }
                    chunks.append(chunk)
        else:
            # Use full document text as single chunk
            chunks = [{
                "chunk_id": "full_document",
                "document_id": document_id,
                "content": document_text,
                "related_criterion": "all",
                "score": 1.0
            }]

        logger.info(f"Retrieved {len(chunks)} document chunks")
        return chunks

    async def _evaluate_criteria_batch(
        self,
        rubric_data: Dict[str, Any],
        document_chunks: List[Dict[str, Any]]
    ) -> List[CriterionEvaluation]:
        """Evaluate all criteria in a single LLM call."""
        if self.llm is None:
            # Return stub evaluations
            return self._create_stub_evaluations(rubric_data)

        try:
            # Prepare document content
            document_content = "\n\n".join([
                f"[Chunk {i+1} - Related to {chunk.get('related_criterion', 'all')}]: {chunk['content']}"
                for i, chunk in enumerate(document_chunks)
            ])

            # Prepare criteria details
            criteria_details = "\n\n".join([
                f"Criterion: {criterion['criterion_id']}\n"
                f"Weight: {criterion['weight']}\n"
                f"Description: {criterion['description']}\n"
                f"Definition: {criterion.get('scoring_criteria', criterion.get('definition', 'Standard 1-5 scale'))}"
                for criterion in rubric_data["criteria"]
            ])

            # Create evaluation chain
            from langchain_core.output_parsers import JsonOutputParser
            chain = self.batch_evaluation_template | self.llm | JsonOutputParser()

            # Run evaluation
            batch_result = await chain.ainvoke({
                "rubric_name": rubric_data["rubric_name"],
                "rubric_description": rubric_data.get("description", ""),
                "criteria_details": criteria_details,
                "document_content": document_content
            })

            # Process results
            evaluations = []
            results_by_name = {
                eval_result["criterion_name"]: eval_result
                for eval_result in batch_result["evaluation"]
            }

            for criterion in rubric_data["criteria"]:
                criterion_id = criterion["criterion_id"]
                criterion_name = criterion.get("name", criterion_id)  # Use name if available, fallback to ID

                if criterion_name in results_by_name:
                    result = results_by_name[criterion_name]
                    evaluation = CriterionEvaluation(
                        criterion_name=criterion_name,
                        criterion_description=criterion["description"],
                        weight=criterion["weight"],
                        score=result["score"],
                        reasoning=result["reasoning"],
                        evidence=result["evidence"]
                    )
                    evaluations.append(evaluation)
                else:
                    # Create default evaluation
                    logger.warning(f"Missing evaluation for criterion: {criterion_name}")
                    evaluation = CriterionEvaluation(
                        criterion_name=criterion_name,
                        criterion_description=criterion["description"],
                        weight=criterion["weight"],
                        score=1.0,
                        reasoning="Evaluation not provided by model",
                        evidence=[]
                    )
                    evaluations.append(evaluation)

            logger.info(f"Completed batch evaluation of {len(evaluations)} criteria")
            return evaluations

        except Exception as e:
            logger.error(f"Error in batch evaluation: {e}")
            return self._create_stub_evaluations(rubric_data)

    async def _create_summary(
        self,
        rubric_name: str,
        criteria_evaluations: List[CriterionEvaluation]
    ) -> Dict[str, Any]:
        """Create evaluation summary."""
        if self.llm is None:
            return {
                "summary": f"Stub evaluation summary for {rubric_name}",
                "strengths": ["Placeholder strength"],
                "improvements": ["Placeholder improvement"]
            }

        try:
            overall_score = self._calculate_overall_score(criteria_evaluations)
            evaluations_summary = "\n".join([
                f"- {eval.criterion_name}: {eval.score}/5.0 - {eval.reasoning[:100]}..."
                for eval in criteria_evaluations
            ])

            from langchain_core.output_parsers import JsonOutputParser
            chain = self.summary_template | self.llm | JsonOutputParser()

            summary_result = await chain.ainvoke({
                "rubric_name": rubric_name,
                "overall_score": overall_score,
                "evaluations_summary": evaluations_summary
            })

            return summary_result

        except Exception as e:
            logger.error(f"Error creating summary: {e}")
            return {
                "summary": f"Error creating summary: {e}",
                "strengths": ["Unable to determine"],
                "improvements": ["Requires manual review"]
            }

    def _calculate_overall_score(self, criteria_evaluations: List[CriterionEvaluation]) -> float:
        """Calculate weighted overall score."""
        if not criteria_evaluations:
            return 0.0

        total_weighted_score = sum(eval.score * eval.weight for eval in criteria_evaluations)
        total_weight = sum(eval.weight for eval in criteria_evaluations)

        return total_weighted_score / total_weight if total_weight > 0 else 0.0

    def _create_stub_evaluations(self, rubric_data: Dict[str, Any]) -> List[CriterionEvaluation]:
        """Create stub evaluations when LLM is not available."""
        evaluations = []
        for criterion in rubric_data["criteria"]:
            criterion_name = criterion.get("name", criterion["criterion_id"])
            evaluation = CriterionEvaluation(
                criterion_name=criterion_name,
                criterion_description=criterion["description"],
                weight=criterion["weight"],
                score=3.0,  # Default middle score
                reasoning=f"Stub evaluation for {criterion_name}",
                evidence=["Placeholder evidence"]
            )
            evaluations.append(evaluation)
        return evaluations

    async def list_rubrics(self) -> List[Dict[str, Any]]:
        """List available rubrics from criteria_api."""
        return await self.criteria_bridge.list_rubrics()


@lru_cache(maxsize=1)
def get_evaluation_service() -> EvaluationService:
    """Get singleton evaluation service instance."""
    criteria_bridge = get_criteria_api_bridge()
    search_service = AzureSearchService()

    return EvaluationService(criteria_bridge, search_service)
