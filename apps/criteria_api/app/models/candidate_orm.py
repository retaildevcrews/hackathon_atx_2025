from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.utils.db import Base


class CandidateORM(Base):
    """Candidate entity.

    Extended to support:
      - description
      - normalized name uniqueness (DB-level)
      - created/updated timestamps
    """
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, index=True)
    name_normalized = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    materials = relationship("CandidateMaterialORM", back_populates="candidate", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('name_normalized', name='uq_candidate_name_normalized'),
    )


class CandidateMaterialORM(Base):
    __tablename__ = "candidate_materials"

    id = Column(String, primary_key=True, index=True)
    candidate_id = Column(String, ForeignKey('candidates.id', ondelete='CASCADE'), index=True, nullable=False)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    blob_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    candidate = relationship("CandidateORM", back_populates="materials")
