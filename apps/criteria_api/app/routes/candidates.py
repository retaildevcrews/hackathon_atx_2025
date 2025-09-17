from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List

from app.models.candidate import (
    Candidate,
    CandidateCreate,
    CandidateUpdate,
    CandidateMaterial,
    CandidateMaterialList,
)
from app.models.evaluation_result import (
    EvaluationResult,
    EvaluationResultCreate,
    EvaluationResultSummary,
    EvaluationResultList,
)
from app.services import candidate_service, candidate_material_service, evaluation_service

router = APIRouter()


@router.get("/", response_model=List[Candidate])
def list_candidates():
    return candidate_service.list_candidates()


@router.post("/", response_model=Candidate, status_code=201)
def create_candidate(data: CandidateCreate):
    """Create a candidate (must supply decisionKitId)."""
    try:
        return candidate_service.create_candidate(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{candidate_id}", response_model=Candidate)
def get_candidate(candidate_id: str):
    c = candidate_service.get_candidate(candidate_id)
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return c


@router.put("/{candidate_id}", response_model=Candidate)
def update_candidate(candidate_id: str, data: CandidateUpdate):
    try:
        return candidate_service.update_candidate(candidate_id, data)
    except ValueError as e:
        msg = str(e)
        if msg == "Candidate not found":
            raise HTTPException(status_code=404, detail=msg)
        if "already exists" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=400, detail=msg)


@router.post("/{candidate_id}/materials", response_model=CandidateMaterial, status_code=201)
def upload_material(candidate_id: str, file: UploadFile = File(...)):
    # ensure candidate exists
    c = candidate_service.get_candidate(candidate_id)
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    try:
        return candidate_material_service.create_material(candidate_id, file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{candidate_id}/materials", response_model=CandidateMaterialList)
def list_materials(candidate_id: str):
    c = candidate_service.get_candidate(candidate_id)
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate_material_service.list_materials(candidate_id)


@router.get("/{candidate_id}/materials/{material_id}", response_model=CandidateMaterial)
def get_material(candidate_id: str, material_id: str):
    c = candidate_service.get_candidate(candidate_id)
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    m = candidate_material_service.get_material(candidate_id, material_id)
    if not m:
        raise HTTPException(status_code=404, detail="Material not found")
    return m


@router.delete("/{candidate_id}/materials/{material_id}", response_model=dict)
def delete_material(candidate_id: str, material_id: str):
    c = candidate_service.get_candidate(candidate_id)
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    deleted = candidate_material_service.delete_material(candidate_id, material_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Material not found")
    return {"success": True}


@router.delete("/{candidate_id}", status_code=204)
def delete_candidate(candidate_id: str):
    """Delete a candidate and all its materials (hard delete).

    Also removes any decision kit associations. Returns 204 on success, 404 if not found.
    """
    deleted = candidate_service.delete_candidate(candidate_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return None


# Evaluation Results Routes

@router.post("/evaluations", response_model=EvaluationResult, status_code=201)
def create_evaluation_result(data: EvaluationResultCreate):
    """Create a new evaluation result.

    This endpoint is used by the agent service to store evaluation results
    and return an evaluation ID for future reference.
    """
    try:
        return evaluation_service.create_evaluation_result(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create evaluation result: {str(e)}")


@router.get("/evaluations", response_model=EvaluationResultList)
def list_evaluation_results(limit: int = 50, offset: int = 0):
    """List evaluation results with pagination."""
    try:
        return evaluation_service.list_evaluation_results(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list evaluation results: {str(e)}")


@router.get("/evaluations/{evaluation_id}", response_model=EvaluationResult)
def get_evaluation_result(evaluation_id: str):
    """Get a specific evaluation result by ID."""
    result = evaluation_service.get_evaluation_result(evaluation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Evaluation result not found")
    return result


@router.get("/{candidate_id}/evaluations", response_model=List[EvaluationResultSummary])
def get_candidate_evaluations(candidate_id: str):
    """Get all evaluation results that include this candidate."""
    # Ensure candidate exists
    c = candidate_service.get_candidate(candidate_id)
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")

    try:
        return evaluation_service.get_evaluation_results_by_candidate(candidate_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get candidate evaluations: {str(e)}")


@router.delete("/evaluations/{evaluation_id}", status_code=204)
def delete_evaluation_result(evaluation_id: str):
    """Delete an evaluation result and all its associations."""
    deleted = evaluation_service.delete_evaluation_result(evaluation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Evaluation result not found")
    return None
