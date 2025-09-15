import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
from app.utils.db import SessionLocal
from app.models.rubric_orm import RubricORM
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


def list_rubrics(db: Optional[Session] = None) -> List[Rubric]:
    close = False
    if db is None:
        db = SessionLocal(); close = True
    rows = db.query(RubricORM).order_by(RubricORM.created_at.desc()).all()
    rubrics = [Rubric(
        id=r.id,
        name=r.name_original,
        description=r.description,
        criteria=r.get_criteria(),
        version=r.version,
        published=r.published,
        publishedAt=r.published_at,
        createdAt=r.created_at,
        updatedAt=r.updated_at,
    ) for r in rows]
    if close:
        db.close()
    return rubrics


def get_rubric_by_id(rubric_id: str) -> Optional[Rubric]:
    db = SessionLocal()
    r = db.query(RubricORM).filter(RubricORM.id == rubric_id).first()
    if not r:
        db.close(); return None
    rubric = Rubric(
        id=r.id,
        name=r.name_original,
        description=r.description,
        criteria=r.get_criteria(),
        version=r.version,
        published=r.published,
        publishedAt=r.published_at,
        createdAt=r.created_at,
        updatedAt=r.updated_at,
    )
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
    orm.set_criteria([c.dict() for c in data.criteria])
    db.add(orm)
    db.commit()
    db.refresh(orm)
    rubric = Rubric(
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
        orm.set_criteria([c.dict() for c in data.criteria])
    orm.updated_at = datetime.utcnow()
    db.commit(); db.refresh(orm)
    rubric = Rubric(
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
    orm.published_at = datetime.utcnow()
    orm.updated_at = datetime.utcnow()
    db.commit(); db.refresh(orm)
    rubric = Rubric(
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
