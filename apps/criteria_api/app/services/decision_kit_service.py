import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from app.utils.db import SessionLocal
from app.models.decision_kit import (
    DecisionKitCreate, DecisionKit, DecisionKitCandidateRef, DecisionKitUpdateCandidates
)
from app.models.decision_kit_orm import DecisionKitORM, DecisionKitCandidateORM
from app.models.candidate_orm import CandidateORM
from app.models.rubric_orm import RubricORM


def _normalize_name(name: str) -> str:
    return name.strip().lower()


def _serialize(orm: DecisionKitORM) -> DecisionKit:
    candidates = [
        DecisionKitCandidateRef(
            id=c.id,
            candidateId=c.candidate_id,
            candidateName=c.candidate_name,
            position=idx,
        ) for idx, c in enumerate(sorted(orm.candidates_assoc, key=lambda x: x.position))
    ]
    return DecisionKit(
        id=orm.id,
        name=orm.name_original,
        description=orm.description,
        rubricId=orm.rubric_id,
        rubricVersion=orm.rubric_version,
        rubricPublished=orm.rubric_published,
        status=orm.status,
        candidates=candidates,
        createdAt=orm.created_at,
        updatedAt=orm.updated_at,
    )


def _validate_candidate_ids(db: Session, ids: List[str]):
    if not ids:
        return
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate candidate ids")
    existing = db.query(CandidateORM.id).filter(CandidateORM.id.in_(ids)).all()
    existing_ids = {row[0] for row in existing}
    missing = [c for c in ids if c not in existing_ids]
    if missing:
        raise ValueError(f"invalid candidate ids: {missing}")


def create_decision_kit(data: DecisionKitCreate) -> DecisionKit:
    db: Session = SessionLocal()
    try:
        norm = _normalize_name(data.name)
        existing = db.query(DecisionKitORM).filter(DecisionKitORM.name_normalized == norm).first()
        if existing:
            raise ValueError("decision kit name exists")
        # load rubric snapshot info
        rubric = db.query(RubricORM).filter(RubricORM.id == data.rubricId).first()
        if not rubric:
            raise ValueError("invalid rubric id")
        _validate_candidate_ids(db, data.candidateIds)
        kit_id = str(uuid.uuid4())
        kit = DecisionKitORM(
            id=kit_id,
            name_normalized=norm,
            name_original=data.name,
            description=data.description,
            rubric_id=rubric.id,
            rubric_version=rubric.version,
            rubric_published=rubric.published,
        )
        db.add(kit)
        db.flush()
        for pos, cid in enumerate(data.candidateIds):
            cand = db.query(CandidateORM).filter(CandidateORM.id == cid).first()
            db.add(DecisionKitCandidateORM(
                id=str(uuid.uuid4()),
                decision_kit_id=kit.id,
                candidate_id=cid,
                candidate_name=cand.name if cand else "",  # cand must exist per validation
                position=pos,
            ))
        db.commit(); db.refresh(kit)
        kit = db.query(DecisionKitORM).options(joinedload(DecisionKitORM.candidates_assoc)).filter(DecisionKitORM.id == kit_id).first()
        return _serialize(kit)
    finally:
        db.close()


def get_decision_kit(kit_id: str) -> Optional[DecisionKit]:
    db = SessionLocal()
    try:
        kit = db.query(DecisionKitORM).options(joinedload(DecisionKitORM.candidates_assoc)).filter(DecisionKitORM.id == kit_id).first()
        if not kit:
            return None
        return _serialize(kit)
    finally:
        db.close()


def list_decision_kits(name_filter: Optional[str] = None) -> List[DecisionKit]:
    db = SessionLocal(); close=True
    try:
        q = db.query(DecisionKitORM).options(joinedload(DecisionKitORM.candidates_assoc))
        if name_filter:
            q = q.filter(DecisionKitORM.name_normalized.contains(name_filter.lower()))
        rows = q.order_by(DecisionKitORM.created_at.desc()).all()
        return [_serialize(r) for r in rows]
    finally:
        if close:
            db.close()


def update_candidates(kit_id: str, data: DecisionKitUpdateCandidates) -> Optional[DecisionKit]:
    db = SessionLocal()
    try:
        kit = db.query(DecisionKitORM).options(joinedload(DecisionKitORM.candidates_assoc)).filter(DecisionKitORM.id == kit_id).first()
        if not kit:
            return None
        if kit.status != "OPEN":
            raise ValueError("kit not open")
        _validate_candidate_ids(db, data.candidateIds)
        # remove existing
        for assoc in list(kit.candidates_assoc):
            db.delete(assoc)
        db.flush()
        for pos, cid in enumerate(data.candidateIds):
            cand = db.query(CandidateORM).filter(CandidateORM.id == cid).first()
            db.add(DecisionKitCandidateORM(
                id=str(uuid.uuid4()),
                decision_kit_id=kit.id,
                candidate_id=cid,
                candidate_name=cand.name if cand else "",
                position=pos,
            ))
        kit.updated_at = datetime.now(timezone.utc)
        db.commit(); db.refresh(kit)
        kit = db.query(DecisionKitORM).options(joinedload(DecisionKitORM.candidates_assoc)).filter(DecisionKitORM.id == kit_id).first()
        return _serialize(kit)
    finally:
        db.close()


def delete_decision_kit(kit_id: str) -> bool:
    db = SessionLocal()
    try:
        kit = db.query(DecisionKitORM).filter(DecisionKitORM.id == kit_id).first()
        if not kit:
            return False
        db.delete(kit)
        db.commit()
        return True
    finally:
        db.close()
