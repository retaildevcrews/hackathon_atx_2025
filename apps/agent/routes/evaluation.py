"""
Routes for document evaluation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from models.invoke import (
    EvaluationRequest,
    EvaluationResponse,
    RubricsListResponse
)
from services.evaluation_service import EvaluationService, get_evaluation_service

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_document(
    request: EvaluationRequest,
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
) -> EvaluationResponse:
    """Evaluate a document against a specific rubric.

    Args:
        request: Evaluation request with document text and rubric name/ID
        evaluation_service: Injected evaluation service

    Returns:
        Evaluation results with scores, reasoning, and recommendations
    """
    try:
        # Support both rubric name and ID lookup
        rubric_identifier = request.rubric_name

        result = await evaluation_service.evaluate_document(
            document_text=request.document_text,
            rubric_name=rubric_identifier,
            document_id=request.document_id,
            max_chunks=request.max_chunks
        )

        if "error" in result:
            return EvaluationResponse(
                status="error",
                error=result["error"]
            )

        # Convert dict to EvaluationResult model
        from models.invoke import EvaluationResult
        evaluation_result = EvaluationResult(**result)

        return EvaluationResponse(
            status="success",
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


@router.get("/health")
async def evaluation_health() -> Dict[str, str]:
    """Health check for evaluation service."""
    return {
        "status": "healthy",
        "service": "evaluation"
    }
