from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class EvaluationResultCreate(BaseModel):
    """Model for creating a new evaluation result."""
    rubric_id: str = Field(..., description="ID of rubric used for evaluation")
    overall_score: float = Field(ge=1.0, le=5.0, description="Overall weighted score")
    rubric_name: str = Field(..., description="Name of rubric used")
    total_candidates: int = Field(ge=1, description="Number of candidates evaluated")
    is_batch: bool = Field(default=False, description="True if multiple candidates were evaluated")

    # Complex data structures
    individual_results: List[Dict[str, Any]] = Field(..., description="Individual evaluation results")
    comparison_summary: Optional[Dict[str, Any]] = Field(None, description="Batch comparison data")

    # Metadata
    evaluation_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    # Candidate associations
    candidate_ids: List[str] = Field(..., description="List of candidate IDs that were evaluated")


class EvaluationResultUpdate(BaseModel):
    """Model for updating evaluation result metadata."""
    evaluation_metadata: Optional[Dict[str, Any]] = None


class EvaluationCandidate(BaseModel):
    """Model for candidate within an evaluation result."""
    id: str
    evaluation_id: str
    candidate_id: str
    candidate_score: float
    rank: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvaluationResult(BaseModel):
    """Model for complete evaluation result."""
    id: str
    rubric_id: str
    overall_score: float
    rubric_name: str
    total_candidates: int
    is_batch: bool
    individual_results: List[Dict[str, Any]]
    comparison_summary: Optional[Dict[str, Any]]
    evaluation_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    # Related data
    candidates: List[EvaluationCandidate] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class EvaluationResultSummary(BaseModel):
    """Simplified evaluation result for listing."""
    id: str
    rubric_id: str
    rubric_name: str
    overall_score: float
    total_candidates: int
    is_batch: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvaluationResultList(BaseModel):
    """Response model for listing evaluation results."""
    total: int
    results: List[EvaluationResultSummary]
