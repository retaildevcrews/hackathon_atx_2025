import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.utils.db import SessionLocal
from app.models.candidate_orm import CandidateORM
from app.models.decision_kit_orm import DecisionKitORM, DecisionKitCandidateORM
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
    try:
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
        # If associating to a decision kit, validate kit existence first
        assoc_kit = None
        if data.decisionKitId:
            assoc_kit = db.query(DecisionKitORM).filter(DecisionKitORM.id == data.decisionKitId).first()
            if not assoc_kit:
                db.rollback()
                raise ValueError("Invalid decision kit id")
            if assoc_kit.status != "OPEN":
                db.rollback()
                raise ValueError("Decision kit not open for modification")
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError("Candidate with that name already exists")
        # If kit provided, append association at end (position = current count)
        if assoc_kit:
            # reload candidate to ensure persistence
            db.refresh(orm)
            current_count = len(assoc_kit.candidates_assoc)
            db.add(DecisionKitCandidateORM(
                id=str(uuid.uuid4()),
                decision_kit_id=assoc_kit.id,
                candidate_id=orm.id,
                position=current_count,
            ))
            assoc_kit.updated_at = datetime.now(timezone.utc)
            db.commit()
        db.refresh(orm)
        return _serialize(orm)
    finally:
        db.close()


# Removed deprecated list_candidates_for_decision_kit alias; use list_candidates directly.
