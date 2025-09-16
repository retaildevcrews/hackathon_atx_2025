import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, UTC
from app.utils.db import SessionLocal
from app.models.rubric_orm import RubricORM
from app.models.rubric_criterion_orm import RubricCriterionORM
from app.models.criteria_orm import CriteriaORM
from app.models.rubric import RubricCreate, RubricUpdate, Rubric, RubricCriteriaEntry


def _normalize_name(name: str) -> str:
    return name.strip().lower()


def _validate_criteria(db: Session, entries: List[RubricCriteriaEntry]):
    if not entries:
        return
    ids = [e.criteriaId for e in entries]
    # detect duplicates
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate criteria ids")
    existing = db.query(CriteriaORM.id).filter(CriteriaORM.id.in_(ids)).all()
    existing_ids = {row[0] for row in existing}
    missing = [c for c in ids if c not in existing_ids]
    if missing:
        raise ValueError(f"invalid criteria ids: {missing}")


def _serialize_rubric(r: RubricORM) -> Rubric:
    criteria_list = r.get_criteria_entries()
    return Rubric(
        id=r.id,
        name=r.name_original,
        description=r.description,
        criteria=criteria_list,
        version=r.version,
        published=r.published,
        publishedAt=r.published_at,
        createdAt=r.created_at,
        updatedAt=r.updated_at,
    )


def list_rubrics(db: Optional[Session] = None) -> List[Rubric]:
    close = False
    if db is None:
        db = SessionLocal(); close = True
    rows = db.query(RubricORM).order_by(RubricORM.created_at.desc()).all()
    rubrics = [_serialize_rubric(r) for r in rows]
    if close:
        db.close()
    return rubrics


def get_rubric_by_id(rubric_id: str) -> Optional[Rubric]:
    db = SessionLocal()
    r = db.query(RubricORM).filter(RubricORM.id == rubric_id).first()
    if not r:
        db.close(); return None
    rubric = _serialize_rubric(r)
    db.close()
    return rubric


def create_rubric(data: RubricCreate) -> Rubric:
    db = SessionLocal()
    norm = _normalize_name(data.name)
    existing = db.query(RubricORM).filter(RubricORM.name_normalized == norm).first()
    if existing:
        db.close()
        raise ValueError("rubric name exists")
    _validate_criteria(db, data.criteria)
    rid = str(uuid.uuid4())
    orm = RubricORM(
        id=rid,
        name_normalized=norm,
        name_original=data.name,
        version="1.0.0",
        description=data.description,
        published=False,
    )
    # Build association rows
    orm.criteria_assoc = []
    for pos, entry in enumerate(data.criteria):
        orm.criteria_assoc.append(RubricCriterionORM(
            id=str(uuid.uuid4()),
            rubric_id=rid,
            criterion_id=entry.criteriaId,
            position=pos,
            weight=entry.weight,
        ))
    # Optionally keep legacy JSON for debugging
    db.add(orm)
    db.commit()
    db.refresh(orm)
    rubric = _serialize_rubric(orm)
    db.close()
    return rubric


def update_rubric(rubric_id: str, data: RubricUpdate) -> Optional[Rubric]:
    db = SessionLocal()
    orm = db.query(RubricORM).filter(RubricORM.id == rubric_id).first()
    if not orm:
        db.close(); return None
    if orm.published:
        db.close(); raise ValueError("rubric immutable")
    if data.description is not None:
        orm.description = data.description
    if data.criteria is not None:
        _validate_criteria(db, data.criteria)
        # Clear existing association rows explicitly so flush removes them
        for existing in list(orm.criteria_assoc):
            db.delete(existing)
        orm.criteria_assoc = []
        db.flush()  # ensure deletes are applied before inserts to avoid unique constraint
        for pos, entry in enumerate(data.criteria):
            orm.criteria_assoc.append(RubricCriterionORM(
                id=str(uuid.uuid4()),
                rubric_id=orm.id,
                criterion_id=entry.criteriaId,
                position=pos,
                weight=entry.weight,
            ))
    # association rows already updated
    orm.updated_at = datetime.now(UTC)
    db.commit(); db.refresh(orm)
    rubric = _serialize_rubric(orm)
    db.close()
    return rubric


def publish_rubric(rubric_id: str) -> Optional[Rubric]:
    db = SessionLocal()
    orm = db.query(RubricORM).filter(RubricORM.id == rubric_id).first()
    if not orm:
        db.close(); return None
    if orm.published:
        db.close(); return Rubric(
            id=orm.id,
            name=orm.name_original,
            description=orm.description,
            criteria=orm.get_criteria(),
            version=orm.version,
            published=orm.published,
            publishedAt=orm.published_at,
            createdAt=orm.created_at,
            updatedAt=orm.updated_at,
        )
    orm.published = True
    orm.published_at = datetime.now(UTC)
    orm.updated_at = datetime.now(UTC)
    db.commit(); db.refresh(orm)
    rubric = _serialize_rubric(orm)
    db.close()
    return rubric


def delete_rubric(rubric_id: str) -> bool:
    db = SessionLocal()
    orm = db.query(RubricORM).filter(RubricORM.id == rubric_id).first()
    if not orm:
        db.close(); return False
    if orm.published:
        db.close(); raise ValueError("rubric immutable")
    db.delete(orm)
    db.commit()
    db.close()
    return True


def is_criterion_referenced(criterion_id: str) -> bool:
    """Return True if any rubric (draft or published) references the given criterion.
    Placeholder for future deletion guard. """
    db = SessionLocal()
    exists = db.query(RubricCriterionORM).filter(RubricCriterionORM.criterion_id == criterion_id).first() is not None
    db.close()
    return exists
