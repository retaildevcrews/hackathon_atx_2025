from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.utils.db import Base


class RubricORM(Base):
    __tablename__ = "rubrics"

    id = Column(String, primary_key=True, index=True)
    name_normalized = Column(String, index=True, nullable=False)  # lowercased for uniqueness check
    name_original = Column(String, nullable=False)
    version = Column(String, nullable=False, default="1.0.0")
    description = Column(Text, nullable=False)
    published = Column(Boolean, default=False, nullable=False)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # New normalized relationship via join table
    criteria_assoc = relationship(
        "RubricCriterionORM",
        back_populates="rubric",
        order_by="RubricCriterionORM.position",
        cascade="all, delete-orphan",
    )

    def get_criteria_entries(self):
        return [rc.to_entry() for rc in self.criteria_assoc]
