"""
Routes for candidate evaluation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from models.invoke import (
    EvaluationRequest,
    EvaluationResponse,
    RubricsListResponse,
    ComparisonMode,
    RankingStrategy
)
from services.evaluation_service import EvaluationService, get_evaluation_service

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_candidates(
    request: EvaluationRequest,
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
) -> EvaluationResponse:
    """Evaluate candidates against a specific rubric using IDs.

    Automatically handles single candidate or batch evaluation based on
    the number of candidate_ids provided.

    Args:
        request: Evaluation request with rubric_id and candidate_id(s)
        evaluation_service: Injected evaluation service

    Returns:
        Evaluation results with scores, reasoning, and recommendations.
        For single candidate: evaluation field populated
        For multiple candidates: batch_result field populated
    """
    try:
        # Validate request
        if not request.candidate_ids:
            return EvaluationResponse(
                status="error",
                is_batch=False,
                error="No candidate IDs provided"
            )

        # Call unified evaluation method
        result = await evaluation_service.evaluate(
            rubric_id=request.rubric_id,
            candidate_ids=request.candidate_ids,
            comparison_mode=request.comparison_mode,
            ranking_strategy=request.ranking_strategy,
            max_chunks=request.max_chunks
        )

        if "error" in result:
            return EvaluationResponse(
                status="error",
                is_batch=len(request.candidate_ids) > 1,
                error=result["error"]
            )

        # Check if we got an evaluation_id (new flow) or full results (fallback)
        if "evaluation_id" in result and result.get("status") == "success":
            # New flow: return just the evaluation ID
            return EvaluationResponse(
                status="success",
                is_batch=len(request.candidate_ids) > 1,
                evaluation_id=result["evaluation_id"]
            )

        # Fallback to old flow with full results
        # Determine response format based on candidate count
        is_batch = len(request.candidate_ids) > 1

        if is_batch:
            # Multiple documents - return batch result
            from models.invoke import BatchEvaluationResult
            batch_result = BatchEvaluationResult(**result)

            return EvaluationResponse(
                status="success",
                is_batch=True,
                batch_result=batch_result
            )
        else:
            # Single document - return individual result
            from models.invoke import EvaluationResult
            evaluation_result = EvaluationResult(**result)

            return EvaluationResponse(
                status="success",
                is_batch=False,
                evaluation=evaluation_result
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.get("/rubrics", response_model=RubricsListResponse)
async def list_rubrics(
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
) -> RubricsListResponse:
    """List all available evaluation rubrics.

    Args:
        evaluation_service: Injected evaluation service

    Returns:
        List of available rubrics with metadata
    """
    try:
        rubrics_data = await evaluation_service.list_rubrics()

        from models.invoke import RubricInfo
        rubrics = [RubricInfo(**rubric) for rubric in rubrics_data]

        return RubricsListResponse(
            status="success",
            rubrics=rubrics
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list rubrics: {str(e)}"
        )


@router.get("/rubrics/{rubric_id}")
async def get_rubric_details(
    rubric_id: str,
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
) -> Dict[str, Any]:
    """Get detailed information about a specific rubric.

    Args:
        rubric_id: ID of the rubric to retrieve
        evaluation_service: Injected evaluation service

    Returns:
        Rubric details with criteria and scoring information
    """
    try:
        rubric_data = await evaluation_service.criteria_bridge.get_rubric(rubric_id)

        if not rubric_data:
            raise HTTPException(
                status_code=404,
                detail=f"Rubric '{rubric_id}' not found"
            )

        return {
            "status": "success",
            "rubric": rubric_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve rubric: {str(e)}"
        )


@router.post("/simple")
async def simple_evaluate(
    rubric_id: str,
    candidate_ids: list[str],
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
) -> Dict[str, str]:
    """Simple evaluation endpoint - just returns evaluation ID.
    
    Args:
        rubric_id: ID of the rubric to use for evaluation
        candidate_ids: List of candidate IDs to evaluate
        evaluation_service: Injected evaluation service
        
    Returns:
        Dictionary with evaluation_id on success or error on failure
    """
    try:
        # Use default settings for simple evaluation
        result = await evaluation_service.evaluate(
            rubric_id=rubric_id,
            candidate_ids=candidate_ids,
            comparison_mode=ComparisonMode.DETERMINISTIC,
            ranking_strategy=RankingStrategy.OVERALL_SCORE,
            max_chunks=5
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        if "evaluation_id" not in result:
            raise HTTPException(status_code=500, detail="Evaluation completed but no ID returned")
            
        return {"evaluation_id": result["evaluation_id"]}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/health")
async def evaluation_health() -> Dict[str, str]:
    """Health check for evaluation service."""
    return {
        "status": "healthy",
        "service": "evaluation"
    }
