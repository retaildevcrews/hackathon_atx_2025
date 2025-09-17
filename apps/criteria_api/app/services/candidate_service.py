import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.utils.db import SessionLocal
from app.models.candidate_orm import CandidateORM
from app.models.candidate import Candidate, CandidateCreate


def _normalize(name: str) -> str:
    return name.strip().lower()


def _serialize(orm: CandidateORM) -> Candidate:
    return Candidate(
        id=orm.id,
        name=orm.name,
        nameNormalized=orm.name_normalized,
        description=orm.description,
        createdAt=orm.created_at,
        updatedAt=orm.updated_at,
    )


def list_candidates() -> List[Candidate]:
    db: Session = SessionLocal()
    rows = db.query(CandidateORM).order_by(CandidateORM.created_at.desc()).all()
    out = [_serialize(r) for r in rows]
    db.close()
    return out


def get_candidate(candidate_id: str) -> Optional[Candidate]:
    db = SessionLocal()
    orm = db.query(CandidateORM).filter(CandidateORM.id == candidate_id).first()
    if not orm:
        db.close(); return None
    c = _serialize(orm)
    db.close()
    return c


def create_candidate(data: CandidateCreate) -> Candidate:
    db = SessionLocal()
    norm = _normalize(data.name)
    # optimistic insert; rely on unique constraint for race conditions
    new_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    orm = CandidateORM(
        id=new_id,
        name_normalized=norm,
        name=data.name,
        description=data.description,
        created_at=now,
        updated_at=now,
    )
    db.add(orm)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        db.close()
        raise ValueError("Candidate with that name already exists")
    db.refresh(orm)
    c = _serialize(orm)
    db.close()
    return c


# Removed deprecated list_candidates_for_decision_kit alias; use list_candidates directly.
