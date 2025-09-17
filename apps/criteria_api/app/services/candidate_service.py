import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.utils.db import SessionLocal
from app.models.candidate_orm import CandidateORM
from app.models.decision_kit_orm import DecisionKitORM, DecisionKitCandidateORM
from app.models.candidate import Candidate, CandidateCreate, CandidateUpdate


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
        # Enforce decisionKitId requirement (greenfield rule)
        if not data.decisionKitId:
            raise ValueError("decisionKitId is required")

        norm = _normalize(data.name)
        kit = db.query(DecisionKitORM).filter(DecisionKitORM.id == data.decisionKitId).first()
        if not kit:
            raise ValueError("Invalid decision kit id")
        if kit.status != "OPEN":
            raise ValueError("Decision kit not open for modification")

        new_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        candidate_orm = CandidateORM(
            id=new_id,
            name_normalized=norm,
            name=data.name,
            description=data.description,
            created_at=now,
            updated_at=now,
        )
        db.add(candidate_orm)
        # Determine position (append)
        current_count = len(kit.candidates_assoc)
        assoc = DecisionKitCandidateORM(
            id=str(uuid.uuid4()),
            decision_kit_id=kit.id,
            candidate_id=new_id,
            position=current_count,
            name_normalized=norm,
        )
        db.add(assoc)
        kit.updated_at = datetime.now(timezone.utc)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            # Likely duplicate per decision kit
            raise ValueError("Candidate name already exists in this decision kit")
        db.refresh(candidate_orm)
        return _serialize(candidate_orm)
    finally:
        db.close()


def update_candidate(candidate_id: str, data: CandidateUpdate) -> Candidate:
    """Update candidate metadata (name, description) enforcing per-kit uniqueness.

    Per-kit uniqueness is enforced by checking existing association rows for the
    candidate's kits (currently exactly one kit expected). If name unchanged, no
    duplicate check beyond early return on same values.
    """
    db = SessionLocal()
    try:
        orm = db.query(CandidateORM).filter(CandidateORM.id == candidate_id).first()
        if not orm:
            raise ValueError("Candidate not found")
        new_norm = _normalize(data.name)
        changed = (new_norm != orm.name_normalized) or (data.description != orm.description)
        if not changed:
            return _serialize(orm)
        # Fetch associated kits to perform per-kit duplicate name check
        # Join via DecisionKitCandidateORM
        assoc_rows = db.query(DecisionKitCandidateORM).filter(DecisionKitCandidateORM.candidate_id == candidate_id).all()
        kit_ids = {a.decision_kit_id for a in assoc_rows}
        if kit_ids:
            # For each kit, ensure no other candidate has same normalized name
            conflict = db.query(DecisionKitCandidateORM).join(CandidateORM, CandidateORM.id == DecisionKitCandidateORM.candidate_id) \
                .filter(DecisionKitCandidateORM.decision_kit_id.in_(kit_ids)) \
                .filter(CandidateORM.name_normalized == new_norm) \
                .filter(CandidateORM.id != candidate_id) \
                .first()
            if conflict:
                raise ValueError("Candidate name already exists in this decision kit")
        # Apply changes
        orm.name = data.name
        orm.name_normalized = new_norm
        orm.description = data.description
        orm.updated_at = datetime.now(timezone.utc)
        # Update association cached normalized name values
        for assoc in assoc_rows:
            assoc.name_normalized = new_norm
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError("Candidate name already exists in this decision kit")
        db.refresh(orm)
        return _serialize(orm)
    finally:
        db.close()

def delete_candidate(candidate_id: str) -> bool:
    """Hard delete a candidate.

    Cascades:
      - CandidateMaterialORM rows (via configured relationship cascade)
    Decision kit associations use RESTRICT on candidate FK; delete them explicitly first.
    Returns True if a row was deleted, False if not found.
    """
    db = SessionLocal()
    try:
        orm = db.query(CandidateORM).filter(CandidateORM.id == candidate_id).first()
        if not orm:
            return False
        # Remove decision kit associations referencing this candidate
        db.query(DecisionKitCandidateORM).filter(DecisionKitCandidateORM.candidate_id == candidate_id).delete(synchronize_session=False)
        db.delete(orm)
        db.commit()
        return True
    finally:
        db.close()
