from __future__ import annotations
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class InvokeRequest(BaseModel):
    prompt: str = Field(..., description="Prompt text to evaluate or process")


class InvokeResponse(BaseModel):
    output: str
    model: str | None = None
    stub: bool | None = None

class CriterionEvaluation(BaseModel):
    """Model for individual criterion evaluation."""
    criterion_id: str
    criterion_description: str
    weight: float
    score: float = Field(ge=1.0, le=5.0, description="Score from 1-5")
    reasoning: str
    evidence: List[str]
    recommendations: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence level 0-1")


class EvaluationRequest(BaseModel):
    """Request model for document evaluation."""
    document_text: str = Field(..., description="Document text to evaluate")
    rubric_name: str = Field(..., description="Name or ID of rubric to use")
    document_id: Optional[str] = Field(None, description="Optional document ID")
    max_chunks: int = Field(default=10, description="Maximum chunks to retrieve")


class EvaluationResult(BaseModel):
    """Model for complete evaluation result from agent."""
    overall_score: float = Field(ge=1.0, le=5.0, description="Overall weighted score")
    document_id: Optional[str] = None
    rubric_name: str
    criteria_evaluations: List[CriterionEvaluation]
    summary: str
    strengths: List[str]
    improvements: List[str]
    agent_metadata: Dict[str, Optional[str]] = Field(default_factory=dict)


class EvaluationResponse(BaseModel):
    """Response model for evaluation endpoint."""
    status: str = Field(description="Success or error status")
    evaluation: Optional[EvaluationResult] = None
    error: Optional[str] = None


class RubricInfo(BaseModel):
    """Model for rubric information (simplified from criteria_api)."""
    rubric_name: str
    rubric_id: str
    domain: str
    version: str
    description: str
    published: bool
    created_at: str


class RubricsListResponse(BaseModel):
    """Response model for listing rubrics."""
    status: str
    rubrics: List[RubricInfo]
