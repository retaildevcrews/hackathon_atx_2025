"""
LangChain-based evaluation service for document assessment against rubrics.
Uses criteria_api service for rubric and criteria data.
"""

import asyncio
import logging
import httpx
from typing import Any, Dict, List, Optional
from functools import lru_cache

from models.invoke import (
    CriterionEvaluation,
    EvaluationResult,
    CandidateInput,
    BatchEvaluationResult,
    ComparisonMode,
    RankingStrategy
)
# Direct criteria API calls - no bridge needed
from services.search_service import AzureSearchService
from services.deterministic_analyzer import DeterministicComparison, get_deterministic_analyzer
from prompts.evaluation_prompts import get_batch_evaluation_template, get_summary_template
from config import get_settings

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for evaluating documents using LangChain/LangGraph."""

    def __init__(
        self,
        search_service: AzureSearchService,
        deterministic_analyzer: Optional[DeterministicComparison] = None,
        llm: Optional[Any] = None
    ):
        """Initialize evaluation service.

        Args:
            search_service: Azure Search service for document chunks
            deterministic_analyzer: Deterministic comparison analyzer
            llm: LangChain LLM instance (will create if None)
        """
        # Initialize settings first
        self.settings = get_settings()

        # Direct criteria API calls
        self.criteria_api_url = self.settings.criteria_api_url.rstrip("/")
        self.search_service = search_service
        self.deterministic_analyzer = deterministic_analyzer or get_deterministic_analyzer()

        # Initialize LLM if not provided
        if llm is None:
            self.llm = self._create_llm()
        else:
            self.llm = llm

        # Get prompt templates
        self.batch_evaluation_template = get_batch_evaluation_template()
        self.summary_template = get_summary_template()

    async def _get_rubric_direct(self, rubric_id: str) -> Optional[Dict[str, Any]]:
        """Get rubric directly from criteria API.

        Args:
            rubric_id: ID of the rubric

        Returns:
            Rubric data or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.criteria_api_url}/rubrics/{rubric_id}")

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                rubric_data = response.json()

                # Transform to evaluation format (simplified)
                return {
                    "rubric_id": rubric_data["id"],
                    "rubric_name": rubric_data["name"],
                    "description": rubric_data["description"],
                    "criteria": [
                        {
                            "criterion_id": criterion["criteriaId"],
                            "name": criterion["name"],
                            "description": criterion["description"],
                            "definition": criterion["definition"],
                            "weight": criterion["weight"]
                        }
                        for criterion in rubric_data["criteria"]
                    ]
                }

        except Exception as e:
            logger.error(f"Error fetching rubric '{rubric_id}' directly: {e}")
            return None

    def _create_llm(self) -> Any:
        """Create LangChain LLM instance."""
        try:
            # Import here to avoid dependency issues if LangChain not installed
            from langchain_openai import AzureChatOpenAI

            # Debug logging
            logger.info(f"Azure OpenAI API Key configured: {bool(self.settings.azure_openai_api_key)}")
            logger.info(f"Azure OpenAI Endpoint: {self.settings.azure_openai_endpoint}")
            logger.info(f"Azure OpenAI Deployment: {self.settings.azure_openai_deployment}")
            logger.info(f"Azure OpenAI API Version: {self.settings.azure_openai_api_version}")

            if not all([
                self.settings.azure_openai_api_key,
                self.settings.azure_openai_endpoint,
                self.settings.azure_openai_deployment
            ]):
                logger.warning("Azure OpenAI not fully configured; using stub LLM")
                logger.warning(f"Missing configs - API Key: {not self.settings.azure_openai_api_key}, "
                             f"Endpoint: {not self.settings.azure_openai_endpoint}, "
                             f"Deployment: {not self.settings.azure_openai_deployment}")
                return None

            logger.info("Creating AzureChatOpenAI instance...")
            llm = AzureChatOpenAI(
                azure_deployment=self.settings.azure_openai_deployment,
                api_key=self.settings.azure_openai_api_key,
                azure_endpoint=self.settings.azure_openai_endpoint,
                api_version=self.settings.azure_openai_api_version,
                temperature=0.1,
                timeout=120
            )
            logger.info("AzureChatOpenAI instance created successfully!")
            return llm
        except ImportError as e:
            logger.warning(f"LangChain not available: {e}; using stub LLM")
            return None
        except Exception as e:
            logger.error(f"Error creating LLM: {e}; using stub LLM")
            return None

    async def save_evaluation_to_criteria_api(
        self,
        evaluation_result: Dict[str, Any],
        rubric_id: str,
        candidate_ids: List[str],
        is_batch: bool = False
    ) -> Optional[str]:
        """Save evaluation result to criteria_api and return evaluation ID.

        Args:
            evaluation_result: The evaluation result dictionary
            rubric_id: ID of the rubric used
            candidate_ids: List of candidate IDs evaluated
            is_batch: Whether this was a batch evaluation

        Returns:
            Evaluation ID if successful, None if failed
        """
        try:
            # Prepare the evaluation data for criteria_api
            if is_batch:
                # Batch evaluation result
                batch_result = evaluation_result
                rubric_name = batch_result.get("rubric_name", "Unknown")
                total_candidates = batch_result.get("total_candidates", len(candidate_ids))

                # Extract overall score from best candidate or calculate average
                overall_score = 3.0  # Default fallback
                if "comparison_summary" in batch_result and "best_candidate" in batch_result["comparison_summary"]:
                    overall_score = batch_result["comparison_summary"]["best_candidate"].get("overall_score", 3.0)
                elif "individual_results" in batch_result and batch_result["individual_results"]:
                    scores = [result.get("overall_score", 3.0) for result in batch_result["individual_results"]]
                    overall_score = sum(scores) / len(scores) if scores else 3.0

                evaluation_data = {
                    "rubric_id": rubric_id,
                    "overall_score": overall_score,
                    "rubric_name": rubric_name,
                    "total_candidates": total_candidates,
                    "is_batch": True,
                    "individual_results": batch_result.get("individual_results", []),
                    "comparison_summary": batch_result.get("comparison_summary"),
                    "evaluation_metadata": batch_result.get("batch_metadata", {}),
                    "candidate_ids": candidate_ids
                }
            else:
                # Single evaluation result
                single_result = evaluation_result
                evaluation_data = {
                    "rubric_id": rubric_id,
                    "overall_score": single_result.get("overall_score", 3.0),
                    "rubric_name": single_result.get("rubric_name", "Unknown"),
                    "total_candidates": 1,
                    "is_batch": False,
                    "individual_results": [single_result],
                    "comparison_summary": None,
                    "evaluation_metadata": single_result.get("agent_metadata", {}),
                    "candidate_ids": candidate_ids
                }

            # Send to criteria_api
            criteria_api_url = self.settings.criteria_api_url or "http://localhost:8000"
            url = f"{criteria_api_url}/candidates/evaluations"

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=evaluation_data)
                response.raise_for_status()

                created_evaluation = response.json()
                evaluation_id = created_evaluation.get("id")

                if evaluation_id:
                    logger.info(f"Successfully saved evaluation result with ID: {evaluation_id}")
                    return evaluation_id
                else:
                    logger.error("No evaluation ID returned from criteria_api")
                    return None

        except Exception as e:
            logger.error(f"Failed to save evaluation to criteria_api: {e}", exc_info=True)
            return None

    async def evaluate(
        self,
        rubric_id: str,
        candidate_ids: List[str],
        comparison_mode: ComparisonMode = ComparisonMode.DETERMINISTIC,
        ranking_strategy: RankingStrategy = RankingStrategy.OVERALL_SCORE,
        max_chunks: int = 10
    ) -> Dict[str, Any]:
        """Evaluate candidates by ID using specified rubric.

        This is the new unified evaluation method that:
        1. Fetches rubric data from criteria_api using rubric_id
        2. Fetches candidate text from Azure Search using candidate_ids
        3. Dispatches to single or batch evaluation based on candidate count

        Args:
            rubric_id: ID of the rubric to use for evaluation
            candidate_ids: List of candidate IDs to evaluate (1 or more)
            comparison_mode: Analysis method for multiple candidates
            ranking_strategy: Strategy for ranking multiple candidates
            max_chunks: Maximum chunks to retrieve per candidate

        Returns:
            Dictionary with evaluation results (single or batch format)
        """
        try:
            # Validate inputs
            if not candidate_ids:
                return {"error": "No candidate IDs provided"}

            if len(candidate_ids) > 20:
                return {"error": f"Too many candidates ({len(candidate_ids)}). Maximum is 20 per batch."}

            # Check for duplicate candidate IDs
            if len(candidate_ids) != len(set(candidate_ids)):
                return {"error": "Candidate IDs must be unique"}

            # Fetch rubric data directly from criteria API
            logger.info(f"Fetching rubric data for rubric_id: {rubric_id}")
            rubric_data = await self._get_rubric_direct(rubric_id)
            if not rubric_data:
                return {"error": f"Rubric '{rubric_id}' not found"}

            # Fetch candidate data
            logger.info(f"Fetching candidate data for {len(candidate_ids)} candidate(s): {candidate_ids}")
            candidates_data = await self.search_service.get_candidates_by_ids(candidate_ids)

            # Check for missing candidates
            missing_candidates = set(candidate_ids) - set(candidates_data.keys())
            if missing_candidates:
                return {"error": f"Candidates not found: {list(missing_candidates)}"}

            # Determine evaluation type based on candidate count
            if len(candidate_ids) == 1:
                # Single candidate evaluation
                candidate_id = candidate_ids[0]
                candidate_data = candidates_data[candidate_id]

                logger.info(f"Performing single candidate evaluation for: {candidate_id}")
                result = await self.evaluate_document(
                    document_text=candidate_data["content"],
                    rubric_name=rubric_id,  # Using rubric_id as rubric_name
                    candidate_id=candidate_id,
                    max_chunks=max_chunks
                )

                # Add metadata about the ID-based workflow
                if "agent_metadata" not in result:
                    result["agent_metadata"] = {}
                result["agent_metadata"]["workflow"] = "id_based"
                result["agent_metadata"]["rubric_id"] = rubric_id
                result["agent_metadata"]["candidate_source"] = "azure_search"

                # Save to criteria_api and return evaluation ID
                evaluation_id = await self.save_evaluation_to_criteria_api(
                    evaluation_result=result,
                    rubric_id=rubric_id,
                    candidate_ids=candidate_ids,
                    is_batch=False
                )

                if evaluation_id:
                    return {"evaluation_id": evaluation_id, "status": "success"}
                else:
                    logger.warning("Failed to save evaluation to criteria_api, returning full result")
                    return result

            else:
                # Batch candidate evaluation
                logger.info(f"Performing batch evaluation for {len(candidate_ids)} candidates")

                # Convert to CandidateInput format for existing batch logic
                candidate_inputs = []
                for candidate_id in candidate_ids:
                    candidate_data = candidates_data[candidate_id]
                    candidate_inputs.append(CandidateInput(
                        candidate_id=candidate_id,
                        candidate_text=candidate_data["content"],
                        metadata=candidate_data.get("metadata", {})
                    ))

                result = await self.evaluate_document_batch(
                    documents=candidate_inputs,
                    rubric_name=rubric_id,  # Using rubric_id as rubric_name
                    comparison_mode=comparison_mode,
                    ranking_strategy=ranking_strategy,
                    max_chunks=max_chunks
                )

                # Add metadata about the ID-based workflow
                if "batch_metadata" not in result:
                    result["batch_metadata"] = {}
                result["batch_metadata"]["workflow"] = "id_based"
                result["batch_metadata"]["rubric_id"] = rubric_id
                result["batch_metadata"]["candidate_source"] = "azure_search"

                # Save to criteria_api and return evaluation ID
                evaluation_id = await self.save_evaluation_to_criteria_api(
                    evaluation_result=result,
                    rubric_id=rubric_id,
                    candidate_ids=candidate_ids,
                    is_batch=True
                )

                if evaluation_id:
                    return {"evaluation_id": evaluation_id, "status": "success"}
                else:
                    logger.warning("Failed to save evaluation to criteria_api, returning full result")
                    return result

        except Exception as e:
            logger.error(f"Evaluation failed: {e}", exc_info=True)
            return {"error": f"Evaluation failed: {str(e)}"}

    async def evaluate_document(
        self,
        document_text: str,
        rubric_name: str,
        candidate_id: Optional[str] = None,
        max_chunks: int = 10
    ) -> Dict[str, Any]:
        """Evaluate a document against a rubric.

        Args:
            document_text: Text content to evaluate
            rubric_name: Name of rubric to use
            candidate_id: Optional document ID for search filtering
            max_chunks: Maximum chunks to retrieve per criterion

        Returns:
            Evaluation results dictionary
        """
        try:
            # Step 1: Load rubric from criteria_api
            rubric_data = await self._get_rubric_direct(rubric_name)
            if not rubric_data:
                return {
                    "error": f"Rubric '{rubric_name}' not found",
                    "overall_score": 0.0,
                    "criteria_evaluations": [],
                    "summary": f"Evaluation failed: Rubric '{rubric_name}' not found"
                }

            # Check if consensus evaluation is enabled
            if self.settings.use_consensus_evaluation:
                logger.info(f"Using CONSENSUS EVALUATION for document {candidate_id}")
                return await self._evaluate_with_consensus(
                    document_text, rubric_data, candidate_id or "unknown"
                )
            else:
                logger.info(f"Using STANDARD EVALUATION for document {candidate_id}")
                return await self._evaluate_standard(
                    document_text, rubric_data, candidate_id, max_chunks
                )

        except Exception as e:
            logger.error(f"Error during document evaluation: {e}")
            return {
                "error": str(e),
                "overall_score": 0.0,
                "criteria_evaluations": [],
                "summary": f"Evaluation failed due to error: {str(e)}"
            }

    async def _evaluate_with_consensus(
        self,
        document_text: str,
        rubric_data: Dict[str, Any],
        candidate_id: str
    ) -> Dict[str, Any]:
        """Evaluate using multi-agent consensus process."""
        from services.consensus_evaluation import ConsensusEvaluationService

        consensus_service = ConsensusEvaluationService(llm=self.llm)

        result = await consensus_service.evaluate_with_consensus(
            candidate_content=document_text,
            rubric_data=rubric_data,
            candidate_id=candidate_id,
            max_rounds=2
        )

        # Add standard metadata
        result["candidate_id"] = candidate_id
        result["rubric_name"] = rubric_data.get("rubric_name", "Unknown")
        if "agent_metadata" not in result:
            result["agent_metadata"] = {}
        result["agent_metadata"]["evaluation_model"] = "multi-agent-consensus"
        result["agent_metadata"]["evaluation_type"] = "debate_style"

        return result

    async def _evaluate_standard(
        self,
        document_text: str,
        rubric_data: Dict[str, Any],
        candidate_id: Optional[str],
        max_chunks: int
    ) -> Dict[str, Any]:
        """Evaluate using standard single-agent process."""
        try:
            rubric_name = rubric_data.get("rubric_name", "Unknown")

            # Step 2: Retrieve document chunks
            document_chunks = await self._retrieve_chunks(
                document_text, rubric_data, candidate_id, max_chunks
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
                candidate_id=candidate_id,
                rubric_name=rubric_name,
                criteria_evaluations=criteria_evaluations,
                summary=summary_data["summary"],
                strengths=summary_data["strengths"],
                improvements=summary_data["improvements"],
                agent_metadata={
                    "evaluation_model": "langchain-azure-openai",
                    "chunks_analyzed": str(len(document_chunks)),  # Convert to string
                    "workflow": "standard_evaluation"
                }
            )

            return result.dict()

        except Exception as e:
            logger.error(f"Error during standard evaluation: {e}")
            return {
                "error": str(e),
                "overall_score": 0.0,
                "criteria_evaluations": [],
                "summary": f"Standard evaluation failed: {e}"
            }

    async def evaluate_document_batch(
        self,
        documents: List[CandidateInput],
        rubric_name: str,
        comparison_mode: ComparisonMode = ComparisonMode.DETERMINISTIC,
        ranking_strategy: RankingStrategy = RankingStrategy.OVERALL_SCORE,
        max_chunks: int = 10
    ) -> Dict[str, Any]:
        """Evaluate multiple documents against a rubric and compare results.

        Args:
            documents: List of documents to evaluate
            rubric_name: Name of rubric to use
            comparison_mode: Method for comparing documents (deterministic, LLM, etc.)
            ranking_strategy: Strategy for ranking documents
            max_chunks: Maximum chunks to retrieve per document

        Returns:
            Batch evaluation results dictionary
        """
        try:
            logger.info(f"Starting batch evaluation of {len(documents)} documents with rubric '{rubric_name}'")

            # Step 1: Validate inputs
            if not documents:
                return {
                    "error": "No documents provided for evaluation",
                    "batch_result": None
                }

            if len(documents) > 20:  # Reasonable limit
                return {
                    "error": f"Too many documents ({len(documents)}). Maximum is 20 per batch.",
                    "batch_result": None
                }

            # Step 2: Evaluate each document in parallel
            logger.info("Evaluating individual documents in parallel...")
            individual_results = await self._evaluate_documents_parallel(
                documents, rubric_name, max_chunks
            )

            # Check if any evaluations failed
            failed_evaluations = [r for r in individual_results if "error" in r]
            if failed_evaluations:
                error_summary = f"{len(failed_evaluations)}/{len(documents)} evaluations failed"
                logger.warning(error_summary)
                # Continue with successful evaluations if any exist
                successful_results = [r for r in individual_results if "error" not in r]
                if not successful_results:
                    return {
                        "error": f"All document evaluations failed. First error: {failed_evaluations[0]['error']}",
                        "batch_result": None
                    }
                individual_results = successful_results

            # Convert dict results to EvaluationResult objects
            evaluation_results = []
            for result_dict in individual_results:
                if "error" not in result_dict:
                    # Convert dict to EvaluationResult for analysis
                    eval_result = EvaluationResult(**result_dict)
                    evaluation_results.append(eval_result)

            # Step 3: Perform cross-document comparison analysis
            logger.info(f"Performing {comparison_mode.value} comparison analysis...")
            comparison_summary = await self._perform_comparison_analysis(
                evaluation_results, comparison_mode, ranking_strategy
            )

            # Step 4: Build batch result
            batch_result = BatchEvaluationResult(
                rubric_name=rubric_name,
                total_candidates=len(documents),
                individual_results=evaluation_results,
                comparison_summary=comparison_summary,
                batch_metadata={
                    "comparison_mode": comparison_mode.value,
                    "ranking_strategy": ranking_strategy.value,
                    "candidates_processed": str(len(evaluation_results)),
                    "candidates_failed": str(len(failed_evaluations)) if failed_evaluations else "0",
                    "evaluation_model": "langchain-azure-openai" if self.llm else "stub"
                }
            )

            logger.info(f"Batch evaluation completed successfully for {len(evaluation_results)} candidates")
            return batch_result.dict()

        except Exception as e:
            logger.error(f"Error during batch evaluation: {e}")
            return {
                "error": str(e),
                "batch_result": None
            }

    async def _evaluate_documents_parallel(
        self,
        documents: List[CandidateInput],
        rubric_name: str,
        max_chunks: int
    ) -> List[Dict[str, Any]]:
        """Evaluate multiple documents in parallel for better performance."""

        # Create evaluation tasks for all documents
        tasks = []
        for doc in documents:
            task = self.evaluate_document(
                document_text=doc.candidate_text,
                rubric_name=rubric_name,
                candidate_id=doc.candidate_id,
                max_chunks=max_chunks
            )
            tasks.append(task)

        # Execute all evaluations in parallel
        logger.info(f"Executing {len(tasks)} document evaluations in parallel...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Document {documents[i].candidate_id} evaluation failed: {result}")
                processed_results.append({
                    "error": str(result),
                    "candidate_id": documents[i].candidate_id
                })
            else:
                processed_results.append(result)

        return processed_results

    async def _perform_comparison_analysis(
        self,
        results: List[EvaluationResult],
        comparison_mode: ComparisonMode,
        ranking_strategy: RankingStrategy
    ) -> Any:
        """Perform comparison analysis based on the specified mode."""

        if comparison_mode == ComparisonMode.DETERMINISTIC:
            # Use deterministic rule-based analysis
            return self.deterministic_analyzer.analyze(results, ranking_strategy)

        elif comparison_mode == ComparisonMode.LLM_ENHANCED:
            # Combine deterministic analysis with LLM insights
            deterministic_analysis = self.deterministic_analyzer.analyze(results, ranking_strategy)

            if self.llm is not None:
                # TODO: Add LLM enhancement in future iteration
                logger.warning("LLM enhancement not yet implemented, using deterministic only")

            return deterministic_analysis

        elif comparison_mode == ComparisonMode.LLM_ONLY:
            # Pure LLM-based analysis
            if self.llm is not None:
                # TODO: Implement LLM-only comparison in future iteration
                logger.warning("LLM-only comparison not yet implemented, falling back to deterministic")
                return self.deterministic_analyzer.analyze(results, ranking_strategy)
            else:
                logger.warning("LLM not available, falling back to deterministic analysis")
                return self.deterministic_analyzer.analyze(results, ranking_strategy)

        else:
            # Default to deterministic
            return self.deterministic_analyzer.analyze(results, ranking_strategy)

    async def _retrieve_chunks(
        self,
        document_text: str,
        rubric_data: Dict[str, Any],
        candidate_id: Optional[str],
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
                        "candidate_id": candidate_id,
                        "content": result.get("content", ""),
                        "related_criterion": criterion["criterion_id"],
                        "score": result.get("score", 0.0)
                    }
                    chunks.append(chunk)
        else:
            # Use full document text as single chunk
            chunks = [{
                "chunk_id": "full_document",
                "candidate_id": candidate_id,
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
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.criteria_api_url}/rubrics/")
                response.raise_for_status()
                rubrics = response.json()

                # Transform to simple list format
                return [
                    {
                        "rubric_name": rubric["name"],
                        "rubric_id": rubric["id"],
                        "domain": "General",  # criteria_api doesn't have domain field
                        "version": rubric["version"],
                        "description": rubric["description"],
                        "published": rubric["published"],
                        "created_at": rubric["createdAt"]
                    }
                    for rubric in rubrics
                ]
        except Exception as e:
            logger.error(f"Error listing rubrics: {e}")
            return []


@lru_cache(maxsize=1)
def get_evaluation_service() -> EvaluationService:
    """Get singleton evaluation service instance."""
    from config import get_settings
    settings = get_settings()

    # Use local search service if enabled, otherwise use Azure Search
    if settings.use_local_search:
        from services.local_search_service import LocalSearchService
        search_service = LocalSearchService()
        logger.info("Using LOCAL SEARCH SERVICE for testing/development")
    else:
        search_service = AzureSearchService()
        logger.info("Using AZURE SEARCH SERVICE for production")

    deterministic_analyzer = get_deterministic_analyzer()

    return EvaluationService(search_service, deterministic_analyzer)
