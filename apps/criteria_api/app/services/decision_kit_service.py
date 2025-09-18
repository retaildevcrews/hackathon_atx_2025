import uuid
from typing import List, Optional, Dict
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from app.utils.db import SessionLocal
from app.models.decision_kit import (
    DecisionKitCreate, DecisionKit, DecisionKitCandidateRef, DecisionKitUpdateCandidates, DecisionKitPatch
)
from app.models.decision_kit_orm import DecisionKitORM, DecisionKitCandidateORM
from app.models.candidate_orm import CandidateORM
from app.models.rubric_orm import RubricORM


def _normalize_name(name: str) -> str:
    return name.strip().lower()


def _serialize(orm: DecisionKitORM) -> DecisionKit:
    candidates = []
    sorted_assoc = sorted(orm.candidates_assoc, key=lambda x: x.position)
    for idx, c in enumerate(sorted_assoc):
        cand_name = c.candidate.name if c.candidate else ""
        candidates.append(DecisionKitCandidateRef(
            id=c.id,
            candidateId=c.candidate_id,
            candidateName=cand_name,
            position=idx,
        ))
    return DecisionKit(
        id=orm.id,
        name=orm.name_original,
        description=orm.description,
        rubricId=orm.rubric_id,
        rubricVersion=orm.rubric_version,
        rubricPublished=orm.rubric_published,
        status=orm.status,
        evaluation_id=orm.evaluation_id,
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
    """Create a decision kit with optional initial candidates.

    Ensures:
      - Kit name uniqueness (global normalized)
      - Candidate IDs are valid
      - Per-kit candidate name uniqueness by populating association.name_normalized
        and surfacing a friendly error on duplicate names.
    """
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

        # Prefetch candidate normalized names for association rows
        cand_map: Dict[str, str] = {}
        if data.candidateIds:
            rows = db.query(CandidateORM.id, CandidateORM.name_normalized).filter(CandidateORM.id.in_(data.candidateIds)).all()
            cand_map = {r[0]: r[1] for r in rows}

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
            db.add(DecisionKitCandidateORM(
                id=str(uuid.uuid4()),
                decision_kit_id=kit.id,
                candidate_id=cid,
                position=pos,
                name_normalized=cand_map.get(cid, ""),
            ))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            # Likely duplicate candidate name within kit
            raise ValueError("duplicate candidate name in decision kit")
        db.refresh(kit)
        kit = db.query(DecisionKitORM).options(
            joinedload(DecisionKitORM.candidates_assoc).joinedload(DecisionKitCandidateORM.candidate)
        ).filter(DecisionKitORM.id == kit_id).first()
        return _serialize(kit)
    finally:
        db.close()


def get_decision_kit(kit_id: str) -> Optional[DecisionKit]:
    db = SessionLocal()
    try:
        kit = db.query(DecisionKitORM).options(
            joinedload(DecisionKitORM.candidates_assoc).joinedload(DecisionKitCandidateORM.candidate)
        ).filter(DecisionKitORM.id == kit_id).first()
        if not kit:
            return None
        return _serialize(kit)
    finally:
        db.close()


def list_decision_kits(name_filter: Optional[str] = None) -> List[DecisionKit]:
    db = SessionLocal(); close=True
    try:
        q = db.query(DecisionKitORM).options(
            joinedload(DecisionKitORM.candidates_assoc).joinedload(DecisionKitCandidateORM.candidate)
        )
        if name_filter:
            q = q.filter(DecisionKitORM.name_normalized.contains(name_filter.lower()))
        rows = q.order_by(DecisionKitORM.created_at.desc()).all()
        return [_serialize(r) for r in rows]
    finally:
        if close:
            db.close()


def update_evaluation_id(kit_id: str, evaluation_id: str) -> Optional[DecisionKit]:
    """Update a decision kit with an evaluation result ID.

    Args:
        kit_id: Decision kit ID to update
        evaluation_id: Evaluation result ID to associate

    Returns:
        Updated decision kit or None if not found
    """
    db = SessionLocal()
    try:
        kit = db.query(DecisionKitORM).options(
            joinedload(DecisionKitORM.candidates_assoc).joinedload(DecisionKitCandidateORM.candidate)
        ).filter(DecisionKitORM.id == kit_id).first()

        if not kit:
            return None

        # Update evaluation_id and timestamp
        kit.evaluation_id = evaluation_id
        kit.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(kit)

        # Re-fetch with relationships for serialization
        kit = db.query(DecisionKitORM).options(
            joinedload(DecisionKitORM.candidates_assoc).joinedload(DecisionKitCandidateORM.candidate)
        ).filter(DecisionKitORM.id == kit_id).first()

        return _serialize(kit)

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def update_candidates(kit_id: str, data: DecisionKitUpdateCandidates) -> Optional[DecisionKit]:
    db = SessionLocal()
    try:
        kit = db.query(DecisionKitORM).options(
            joinedload(DecisionKitORM.candidates_assoc).joinedload(DecisionKitCandidateORM.candidate)
        ).filter(DecisionKitORM.id == kit_id).first()
        if not kit:
            return None
        if kit.status != "OPEN":
            raise ValueError("kit not open")
        _validate_candidate_ids(db, data.candidateIds)

        # Prefetch candidate normalized names
        cand_map: Dict[str, str] = {}
        if data.candidateIds:
            rows = db.query(CandidateORM.id, CandidateORM.name_normalized).filter(CandidateORM.id.in_(data.candidateIds)).all()
            cand_map = {r[0]: r[1] for r in rows}

        # remove existing associations
        for assoc in list(kit.candidates_assoc):
            db.delete(assoc)
        db.flush()
        for pos, cid in enumerate(data.candidateIds):
            db.add(DecisionKitCandidateORM(
                id=str(uuid.uuid4()),
                decision_kit_id=kit.id,
                candidate_id=cid,
                position=pos,
                name_normalized=cand_map.get(cid, ""),
            ))
        kit.updated_at = datetime.now(timezone.utc)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError("duplicate candidate name in decision kit")
        db.refresh(kit)
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


def patch_decision_kit(kit_id: str, data: DecisionKitPatch) -> Optional[DecisionKit]:
    db = SessionLocal()
    try:
        kit = db.query(DecisionKitORM).options(
            joinedload(DecisionKitORM.candidates_assoc).joinedload(DecisionKitCandidateORM.candidate)
        ).filter(DecisionKitORM.id == kit_id).first()
        if not kit:
            return None

        changed = False
        # Update name if provided
        if data.name is not None and data.name != kit.name_original:
            norm = _normalize_name(data.name)
            # check uniqueness
            exists = db.query(DecisionKitORM.id).filter(DecisionKitORM.name_normalized == norm, DecisionKitORM.id != kit_id).first()
            if exists:
                raise ValueError("decision kit name exists")
            kit.name_original = data.name
            kit.name_normalized = norm
            changed = True

        # Update description if provided
        if data.description is not None and data.description != kit.description:
            kit.description = data.description
            changed = True

        # Update rubric snapshot if rubricId provided
        if data.rubricId is not None and data.rubricId != kit.rubric_id:
            rubric = db.query(RubricORM).filter(RubricORM.id == data.rubricId).first()
            if not rubric:
                raise ValueError("invalid rubric id")
            kit.rubric_id = rubric.id
            kit.rubric_version = rubric.version
            kit.rubric_published = rubric.published
            changed = True

        if changed:
            kit.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(kit)

        # Re-fetch with relationships for serialization
        kit = db.query(DecisionKitORM).options(
            joinedload(DecisionKitORM.candidates_assoc).joinedload(DecisionKitCandidateORM.candidate)
        ).filter(DecisionKitORM.id == kit_id).first()
        return _serialize(kit)
    finally:
        db.close()
