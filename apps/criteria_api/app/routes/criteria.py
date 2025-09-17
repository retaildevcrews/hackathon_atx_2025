from fastapi import APIRouter, HTTPException
from typing import List
from app.models.criteria import Criteria, CriteriaCreate, CriteriaUpdate
from app.services import criteria_service

router = APIRouter()

@router.get("/", response_model=List[Criteria])
def get_criteria():
    return criteria_service.list_criteria()

@router.get("/{criteria_id}", response_model=Criteria)
def get_criteria_by_id(criteria_id: str):
    result = criteria_service.get_criteria_by_id(criteria_id)
    if not result:
        raise HTTPException(status_code=404, detail="Criteria not found")
    return result

@router.post("/", response_model=Criteria, status_code=201)
def create_criteria(data: CriteriaCreate):
    return criteria_service.create_criteria(data)

@router.put("/{criteria_id}", response_model=Criteria)
def update_criteria(criteria_id: str, data: CriteriaUpdate):
    updated = criteria_service.update_criteria(criteria_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Criteria not found")
    return updated

# Support update semantics without an ID in the path by treating it as a blank ID update
# This enables clients that send PUT requests with no criteria_id to initialize a new record.
@router.put("/", response_model=Criteria)
def update_criteria_without_id(data: CriteriaUpdate):
    updated = criteria_service.update_criteria("", data)
    # update_criteria will create a new record when criteria_id is blank-like
    return updated

@router.delete("/{criteria_id}", response_model=dict)
def delete_criteria(criteria_id: str):
    deleted = criteria_service.delete_criteria(criteria_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Criteria not found")
    return {"success": True}
