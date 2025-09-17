from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Integer, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.utils.db import Base


class DecisionKitORM(Base):
    __tablename__ = "decision_kits"

    id = Column(String, primary_key=True, index=True)
    name_normalized = Column(String, index=True, nullable=False)
    name_original = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    rubric_id = Column(String, ForeignKey("rubrics.id", ondelete="RESTRICT"), nullable=False)
    rubric_version = Column(String, nullable=False)
    rubric_published = Column(Boolean, nullable=False, default=False)
    status = Column(String, nullable=False, default="OPEN")  # OPEN, CLOSED, ARCHIVED (future)
    evaluation_id = Column(String, ForeignKey("evaluation_results.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    candidates_assoc = relationship(
        "DecisionKitCandidateORM",
        back_populates="decision_kit",
        cascade="all, delete-orphan",
        order_by="DecisionKitCandidateORM.position",
    )

    evaluation = relationship("EvaluationResultORM", lazy="joined")


class DecisionKitCandidateORM(Base):
    __tablename__ = "decision_kit_candidates"

    id = Column(String, primary_key=True, index=True)
    decision_kit_id = Column(String, ForeignKey("decision_kits.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="RESTRICT"), nullable=False)
    position = Column(Integer, nullable=False)

    decision_kit = relationship("DecisionKitORM", back_populates="candidates_assoc")
    candidate = relationship("CandidateORM", lazy="joined")

    __table_args__ = (
    UniqueConstraint("decision_kit_id", "candidate_id", name="uq_decision_kit_candidate"),
        Index("ix_decision_kit_position", "decision_kit_id", "position"),
    )
