from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from app.utils.db import Base


class RubricCriterionORM(Base):
    __tablename__ = "rubric_criteria"

    id = Column(String, primary_key=True, index=True)
    rubric_id = Column(String, ForeignKey("rubrics.id", ondelete="CASCADE"), nullable=False, index=True)
    criterion_id = Column(String, ForeignKey("criteria.id", ondelete="RESTRICT"), nullable=False)
    position = Column(Integer, nullable=False)
    weight = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    rubric = relationship("RubricORM", back_populates="criteria_assoc")

    __table_args__ = (
        UniqueConstraint("rubric_id", "criterion_id", name="uq_rubric_criterion"),
        Index("ix_rubric_position", "rubric_id", "position"),
    )

    def to_entry(self):
        return {"criteriaId": self.criterion_id, "weight": self.weight}
