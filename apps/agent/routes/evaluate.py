from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from services.evaluation_service import get_evaluation_service, EvaluationService

router = APIRouter()


class EvaluateRequest(BaseModel):
    document_url: Optional[str] = Field(default=None, description="Placeholder; currently ignored")
    rubric_name: Optional[str] = Field(default=None)
    model_params: Optional[Dict[str, Any]] = None
    max_concurrency: Optional[int] = Field(default=None, ge=1, le=20)


class CriterionResult(BaseModel):
    criterion_id: str
    criterion_name: str
    criterion_description: str | None
    criterion_definition: Dict[str, Any] | None
    weight: str | None
    score: int | None
    reasoning: str
    evidence: str
    document_chunk: Any | None


class EvaluateResponse(BaseModel):
    rubric_id: str
    rubric_name: str
    criteria: list[CriterionResult]
    model_params: Dict[str, Any]
    system_prompt_template: str


@router.post("/evaluate_rubric", response_model=EvaluateResponse)
async def evaluate_rubric(
    req: EvaluateRequest,
    service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluateResponse:
    try:
        data = await service.evaluate(
            rubric_name=req.rubric_name or "tv_rubric",
            model_params=req.model_params or {},
            max_concurrency=req.max_concurrency or 5,
        )
    except ValueError as ve:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except RuntimeError as re:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(re)) from re
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"evaluation_failed: {exc}") from exc
    return EvaluateResponse(**data)
