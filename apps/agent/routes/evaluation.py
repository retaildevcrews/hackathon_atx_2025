"""
Routes for document evaluation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from models.invoke import (
    EvaluationRequest,
    EvaluationResponse,
    RubricsListResponse,
    BatchEvaluationRequest,
    BatchEvaluationResponse
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


@router.post("/evaluate-batch", response_model=BatchEvaluationResponse)
async def evaluate_document_batch(
    request: BatchEvaluationRequest,
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
) -> BatchEvaluationResponse:
    """Evaluate multiple documents against a rubric and compare results.

    Args:
        request: Batch evaluation request with documents, rubric, and comparison settings
        evaluation_service: Injected evaluation service

    Returns:
        Batch evaluation results with individual scores and cross-document analysis
    """
    try:
        # Validate request
        if not request.documents:
            return BatchEvaluationResponse(
                status="error",
                error="No documents provided for evaluation"
            )

        if len(request.documents) > 20:
            return BatchEvaluationResponse(
                status="error",
                error=f"Too many documents ({len(request.documents)}). Maximum is 20 per batch."
            )

        # Validate document IDs are unique
        document_ids = [doc.document_id for doc in request.documents]
        if len(document_ids) != len(set(document_ids)):
            return BatchEvaluationResponse(
                status="error",
                error="Document IDs must be unique within a batch"
            )

        # Perform batch evaluation
        result = await evaluation_service.evaluate_document_batch(
            documents=request.documents,
            rubric_name=request.rubric_name,
            comparison_mode=request.comparison_mode,
            ranking_strategy=request.ranking_strategy,
            max_chunks=request.max_chunks
        )

        if "error" in result:
            return BatchEvaluationResponse(
                status="error",
                error=result["error"]
            )

        # Convert dict to BatchEvaluationResult model
        from models.invoke import BatchEvaluationResult
        batch_result = BatchEvaluationResult(**result)

        return BatchEvaluationResponse(
            status="success",
            batch_result=batch_result
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch evaluation failed: {str(e)}"
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
