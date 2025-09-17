from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.utils.db import Base


class EvaluationResultORM(Base):
    """Evaluation result entity for storing agent evaluation outputs."""
    __tablename__ = "evaluation_results"

    id = Column(String, primary_key=True, index=True)
    rubric_id = Column(String, ForeignKey("rubrics.id", ondelete="RESTRICT"), nullable=False)
    overall_score = Column(Float, nullable=False)
    rubric_name = Column(String, nullable=False)
    total_candidates = Column(Integer, nullable=False, default=1)
    is_batch = Column(String, nullable=False, default="false")  # "true" or "false" for compatibility

    # Store JSON data for complex structures
    individual_results = Column(JSON, nullable=False)  # List of individual evaluation results
    comparison_summary = Column(JSON, nullable=True)   # Batch comparison data (null for single evaluations)

    # Metadata
    evaluation_metadata = Column(JSON, nullable=True)  # Agent metadata, batch metadata, etc.

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    rubric = relationship("RubricORM", lazy="joined")


class EvaluationCandidateORM(Base):
    """Junction table linking evaluation results to specific candidates."""
    __tablename__ = "evaluation_candidates"

    id = Column(String, primary_key=True, index=True)
    evaluation_id = Column(String, ForeignKey("evaluation_results.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="RESTRICT"), nullable=False)
    candidate_score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=True)  # Rank within the evaluation (1 = best)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    evaluation = relationship("EvaluationResultORM")
    candidate = relationship("CandidateORM", lazy="joined")
