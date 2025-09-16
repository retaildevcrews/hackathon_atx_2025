from fastapi import APIRouter, HTTPException
from typing import List
from app.models.rubric import Rubric, RubricCreate, RubricUpdate
from app.services import rubric_service

router = APIRouter()


@router.get("/", response_model=List[Rubric])
def list_rubrics():
    return rubric_service.list_rubrics()


@router.get("/{rubric_id}", response_model=Rubric)
def get_rubric(rubric_id: str):
    r = rubric_service.get_rubric_by_id(rubric_id)
    if not r:
        raise HTTPException(status_code=404, detail="Rubric not found")
    return r


@router.post("/", response_model=Rubric, status_code=201)
def create_rubric(payload: RubricCreate):
    try:
        return rubric_service.create_rubric(payload)
    except ValueError as e:
        msg = str(e)
        if "exists" in msg:
            raise HTTPException(status_code=409, detail="Rubric name exists")
        raise HTTPException(status_code=400, detail=msg)


@router.put("/{rubric_id}", response_model=Rubric)
def update_rubric(rubric_id: str, payload: RubricUpdate):
    try:
        r = rubric_service.update_rubric(rubric_id, payload)
    except ValueError as e:
        if "immutable" in str(e):
            raise HTTPException(status_code=409, detail="Rubric already published")
        raise HTTPException(status_code=400, detail=str(e))
    if not r:
        raise HTTPException(status_code=404, detail="Rubric not found")
    return r


@router.post("/{rubric_id}/publish", response_model=Rubric)
def publish_rubric(rubric_id: str):
    r = rubric_service.publish_rubric(rubric_id)
    if not r:
        raise HTTPException(status_code=404, detail="Rubric not found")
    return r


@router.delete("/{rubric_id}", status_code=204)
def delete_rubric(rubric_id: str):
    try:
        ok = rubric_service.delete_rubric(rubric_id)
    except ValueError as e:
        if "immutable" in str(e):
            raise HTTPException(status_code=409, detail="Rubric already published")
        raise HTTPException(status_code=400, detail=str(e))
    if not ok:
        raise HTTPException(status_code=404, detail="Rubric not found")
    return None
