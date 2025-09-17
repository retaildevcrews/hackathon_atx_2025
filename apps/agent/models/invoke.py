from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from enum import Enum

from pydantic import BaseModel, Field


class InvokeRequest(BaseModel):
    prompt: str = Field(..., description="Prompt text to evaluate or process")


class InvokeResponse(BaseModel):
    output: str
    model: str | None = None
    stub: bool | None = None


class ComparisonMode(str, Enum):
    """Different modes for comparing multiple candidates."""
    DETERMINISTIC = "deterministic"  # Rule-based analysis
    LLM_ENHANCED = "llm_enhanced"    # LLM + deterministic
    LLM_ONLY = "llm_only"           # Pure LLM analysis


class RankingStrategy(str, Enum):
    """Different strategies for ranking candidates."""
    OVERALL_SCORE = "overall_score"          # Weighted average
    CONSISTENCY = "consistency"              # Lowest std deviation
    PEAK_PERFORMANCE = "peak_performance"    # Highest individual criteria scores
    BALANCED = "balanced"                    # Best across all criteria


class CandidateInput(BaseModel):
    """Input model for a single candidate in batch evaluation."""
    candidate_id: str = Field(..., description="Unique identifier for the candidate")
    candidate_text: str = Field(..., description="Candidate text content to evaluate")
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict, description="Optional candidate metadata")


class StatisticalSummary(BaseModel):
    """Statistical analysis of evaluation results."""
    mean_score: float = Field(description="Average score across all candidates")
    median_score: float = Field(description="Median score across all candidates")
    std_deviation: float = Field(description="Standard deviation of scores")
    score_range: Tuple[float, float] = Field(description="Min and max scores")
    outliers: List[str] = Field(default_factory=list, description="Candidate IDs with outlier scores")


class CriteriaAnalysis(BaseModel):
    """Analysis of performance for a specific criterion across candidates."""
    criterion_name: str = Field(description="Name of the criterion")
    best_candidate_id: str = Field(description="Candidate with highest score for this criterion")
    worst_candidate_id: str = Field(description="Candidate with lowest score for this criterion")
    score_spread: float = Field(description="Difference between highest and lowest scores")
    average_score: float = Field(description="Average score for this criterion")
    performance_trend: str = Field(description="consistent, varied, or polarized")


class CandidateRanking(BaseModel):
    """Ranking information for a single candidate."""
    candidate_id: str = Field(description="Candidate identifier")
    rank: int = Field(description="Rank position (1 = best)")
    overall_score: float = Field(ge=1.0, le=5.0, description="Overall weighted score")
    key_strengths: List[str] = Field(default_factory=list, description="Top performing criteria")
    key_weaknesses: List[str] = Field(default_factory=list, description="Lowest performing criteria")
    score_breakdown: Dict[str, float] = Field(default_factory=dict, description="Score by criterion")


class ComparisonSummary(BaseModel):
    """Summary of cross-candidate comparison analysis."""
    best_candidate: CandidateRanking = Field(description="Top-ranked candidate")
    rankings: List[CandidateRanking] = Field(description="All candidates ranked")
    statistical_summary: StatisticalSummary = Field(description="Statistical analysis")
    criteria_analysis: List[CriteriaAnalysis] = Field(description="Per-criterion analysis")
    cross_candidate_insights: str = Field(description="Insights from comparing candidates")
    recommendation_rationale: str = Field(description="Why the best candidate was chosen")
    analysis_method: ComparisonMode = Field(description="Method used for analysis")


class CriterionEvaluation(BaseModel):
    """Model for individual criterion evaluation."""
    criterion_name: str
    criterion_description: str
    weight: float
    score: float = Field(ge=1.0, le=5.0, description="Score from 1-5")
    reasoning: str
    evidence: List[str]


class EvaluationRequest(BaseModel):
    """Request model for candidate evaluation using IDs."""
    rubric_id: str = Field(..., description="ID of rubric to use for evaluation")
    candidate_ids: List[str] = Field(..., description="List of candidate IDs to evaluate (single or multiple)")
    comparison_mode: ComparisonMode = Field(default=ComparisonMode.DETERMINISTIC, description="Comparison analysis method for multiple candidates")
    ranking_strategy: RankingStrategy = Field(default=RankingStrategy.OVERALL_SCORE, description="Strategy for ranking multiple candidates")
    max_chunks: int = Field(default=10, description="Maximum chunks to retrieve per candidate")


# Removed BatchEvaluationRequest - now using unified EvaluationRequest for both single and batch scenarios


class EvaluationResult(BaseModel):
    """Model for complete evaluation result from agent."""
    overall_score: float = Field(ge=1.0, le=5.0, description="Overall weighted score")
    candidate_id: Optional[str] = None
    rubric_name: str
    criteria_evaluations: List[CriterionEvaluation]
    summary: str
    strengths: List[str]
    improvements: List[str]
    agent_metadata: Dict[str, Optional[str]] = Field(default_factory=dict)


class BatchEvaluationResult(BaseModel):
    """Model for complete batch evaluation result."""
    rubric_name: str = Field(description="Rubric used for evaluation")
    total_candidates: int = Field(description="Number of candidates evaluated")
    individual_results: List[EvaluationResult] = Field(description="Individual evaluation results")
    comparison_summary: ComparisonSummary = Field(description="Cross-candidate comparison analysis")
    batch_metadata: Dict[str, Optional[str]] = Field(default_factory=dict, description="Batch processing metadata")


class EvaluationResponse(BaseModel):
    """Response model for evaluation endpoint - handles both single and batch results."""
    status: str = Field(description="Success or error status")
    is_batch: bool = Field(description="True if multiple candidates were evaluated")
    evaluation_id: Optional[str] = Field(None, description="ID of saved evaluation result")
    evaluation: Optional[EvaluationResult] = Field(None, description="Single candidate evaluation result (fallback)")
    batch_result: Optional[BatchEvaluationResult] = Field(None, description="Batch evaluation result for multiple candidates (fallback)")
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
