from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List

from app.models.candidate import (
    Candidate,
    CandidateCreate,
    CandidateMaterial,
    CandidateMaterialList,
)
from app.services import candidate_service, candidate_material_service

router = APIRouter()


@router.get("/", response_model=List[Candidate])
def list_candidates():
    return candidate_service.list_candidates()


@router.post("/", response_model=Candidate, status_code=201)
def create_candidate(data: CandidateCreate):
    """Create a candidate.

    If decisionKitId is provided in the payload, the new candidate will be
    appended to that decision kit's candidate list (position = last).
    """
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
