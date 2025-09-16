from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.decision_kit import (
    DecisionKit, DecisionKitCreate, DecisionKitUpdateCandidates
)
from app.services import decision_kit_service

router = APIRouter()


@router.get("/", response_model=List[DecisionKit])
def list_kits(name: Optional[str] = Query(None, description="Name filter (contains, case-insensitive)")):
    return decision_kit_service.list_decision_kits(name_filter=name)


@router.get("/{kit_id}", response_model=DecisionKit)
def get_kit(kit_id: str):
    kit = decision_kit_service.get_decision_kit(kit_id)
    if not kit:
        raise HTTPException(status_code=404, detail="Decision Kit not found")
    return kit


@router.post("/", response_model=DecisionKit, status_code=201)
def create_kit(payload: DecisionKitCreate):
    try:
        return decision_kit_service.create_decision_kit(payload)
    except ValueError as e:
        msg = str(e)
        if "exists" in msg:
            raise HTTPException(status_code=409, detail="Decision Kit name exists")
        if "invalid rubric id" in msg:
            raise HTTPException(status_code=422, detail="Invalid rubric id")
        if "invalid candidate ids" in msg:
            raise HTTPException(status_code=422, detail=msg)
        raise HTTPException(status_code=400, detail=msg)


@router.put("/{kit_id}/candidates", response_model=DecisionKit)
def update_kit_candidates(kit_id: str, payload: DecisionKitUpdateCandidates):
    try:
        kit = decision_kit_service.update_candidates(kit_id, payload)
    except ValueError as e:
        if "not open" in str(e):
            raise HTTPException(status_code=409, detail="Decision Kit not open")
        if "invalid candidate ids" in str(e):
            raise HTTPException(status_code=422, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    if not kit:
        raise HTTPException(status_code=404, detail="Decision Kit not found")
    return kit


@router.delete("/{kit_id}", status_code=204)
def delete_kit(kit_id: str):
    ok = decision_kit_service.delete_decision_kit(kit_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Decision Kit not found")
    return None
