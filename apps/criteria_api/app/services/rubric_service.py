import uuid
from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.utils.db import SessionLocal
from app.models.rubric_orm import RubricORM
from app.models.rubric_criterion_orm import RubricCriterionORM
from app.models.criteria_orm import CriteriaORM
from app.models.rubric import RubricCreate, RubricUpdate, Rubric, RubricCriteriaEntry, RubricCriteriaEntryCreate
from app.config import settings
import math


def _normalize_name(name: str) -> str:
    return name.strip().lower()


class RubricValidationError(ValueError):
    def __init__(self, code: str, detail: str = "", **ctx):  # context for error mapping
        self.code = code
        self.detail = detail
        self.ctx = ctx
        super().__init__(detail or code)


def _normalize_and_validate_entries(db: Session, entries: List[RubricCriteriaEntryCreate], existing_weights: Optional[Dict[str, float]] = None):
    if not entries:
        return []
    ids_seen = set()
    normalized: List[RubricCriteriaEntry] = []
    for idx, e in enumerate(entries):
        cid = e.criteriaId
        # Initialize missing or blank criteria IDs by creating a new criteria row
        if not cid or str(cid).strip() in ("", "null", "undefined"):
            # Require a name to create new criteria; fall back to a generated placeholder if absent
            new_name = e.name or f"Untitled Criterion {idx+1}"
            new_desc = e.description or ""
            new_def = e.definition or ""
            new_cid = str(uuid.uuid4())
            new_orm = CriteriaORM(id=new_cid, name=new_name, description=new_desc, definition=new_def)
            db.add(new_orm)
            db.flush()
            cid = new_cid
        if cid in ids_seen:
            raise RubricValidationError("DUPLICATE_CRITERIA", criteria_id=cid, index=idx)
        ids_seen.add(cid)
        weight = e.weight
        if weight is None:
            # Preserve prior weight if available for this criteriaId (update flow)
            if existing_weights is not None and cid and cid in existing_weights:
                weight = existing_weights[cid]
            else:
                weight = settings.DEFAULT_RUBRIC_WEIGHT
        # Type / numeric validation
        if not isinstance(weight, (int, float)) or isinstance(weight, bool):
            raise RubricValidationError("INVALID_WEIGHT", detail="weight must be numeric", index=idx)
        if not math.isfinite(weight):
            raise RubricValidationError("INVALID_WEIGHT", detail="weight must be finite", index=idx)
        # Normalize to float
        weight = float(weight)
        # Enforce configurable product rule: min..max inclusive, in step increments
        min_w = settings.RUBRIC_WEIGHT_MIN
        max_w = settings.RUBRIC_WEIGHT_MAX
        step = settings.RUBRIC_WEIGHT_STEP
        if weight < min_w or weight > max_w:
            raise RubricValidationError(
                "INVALID_WEIGHT",
                detail=f"weight must be between {min_w} and {max_w}",
                index=idx,
            )
        n = round(weight / step)
        if abs(weight - (n * step)) > 1e-9:
            raise RubricValidationError(
                "INVALID_WEIGHT",
                detail=f"weight must be in {step} increments",
                index=idx,
            )
        # Append for each entry
        normalized.append(RubricCriteriaEntry(criteriaId=cid, weight=weight))

    # Validate existence of criteria ids
    existing = db.query(CriteriaORM.id).filter(CriteriaORM.id.in_([n.criteriaId for n in normalized])).all()
    existing_ids = {row[0] for row in existing}
    missing = [n.criteriaId for n in normalized if n.criteriaId not in existing_ids]
    if missing:
        raise RubricValidationError("INVALID_CRITERIA", detail=f"invalid criteria ids: {missing}")
    # Enforce that weights sum to 1.0 (within tolerance)
    total = sum(float(n.weight) for n in normalized)
    if abs(total - 1.0) > 1e-6:
        raise RubricValidationError("INVALID_WEIGHT_SUM", detail=f"weights must sum to 1.0 (got {total:.6f})")
    return normalized


def _serialize_rubric(r: RubricORM, db: Optional[Session] = None) -> Rubric:
    # Original lightweight entries
    base_entries = r.get_criteria_entries()  # List[RubricCriteriaEntry]
    # Fetch all referenced criteria to enrich with name/description/definition
    enrich_map = {}
    if base_entries:
        close = False
        if db is None:
            db = SessionLocal(); close = True
        # Support both dict-based (from to_entry()) and Pydantic model entries
        ids = [ (e.get('criteriaId') if isinstance(e, dict) else getattr(e, 'criteriaId', None)) for e in base_entries ]
        rows = db.query(CriteriaORM).filter(CriteriaORM.id.in_(ids)).all()
        enrich_map = {row.id: row for row in rows}
        if close:
            db.close()
    # Build enriched entries (still conforming to RubricCriteriaEntry but we add extra attrs dynamically)
    enriched = []
    for e in base_entries:
        # e may already be a dict from RubricCriterionORM.to_entry()
        if isinstance(e, dict):
            criteria_id = e.get('criteriaId')
            weight_val = e.get('weight')
        else:  # Pydantic model
            criteria_id = getattr(e, 'criteriaId', None)
            weight_val = getattr(e, 'weight', None)
        orm = enrich_map.get(criteria_id)
        data = {
            'criteriaId': criteria_id,
            'weight': weight_val,
            'name': getattr(orm, 'name', None) if orm else None,
            'description': getattr(orm, 'description', None) if orm else None,
            'definition': getattr(orm, 'definition', None) if orm else None,
        }
        enriched.append(RubricCriteriaEntry(**data))
    return Rubric(
        id=r.id,
        name=r.name_original,
        description=r.description,
        criteria=enriched,
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
    rubrics = [_serialize_rubric(r, db) for r in rows]
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
        # Upsert behavior: if an unpublished rubric with the same name exists, update it instead of erroring
        if existing.published:
            db.close()
            raise ValueError("rubric name exists and is published")
        # Update existing draft rubric
        normalized_entries = _normalize_and_validate_entries(db, data.criteria)
        # Keep display and normalized names in sync with the latest payload
        existing.name_original = data.name
        existing.name_normalized = norm
        if data.description is not None:
            existing.description = data.description
        # Replace association rows
        for assoc in list(existing.criteria_assoc):
            db.delete(assoc)
        existing.criteria_assoc = []
        db.flush()
        for pos, entry in enumerate(normalized_entries):
            existing.criteria_assoc.append(RubricCriterionORM(
                id=str(uuid.uuid4()),
                rubric_id=existing.id,
                criterion_id=entry.criteriaId,
                position=pos,
                weight=entry.weight,
            ))
        existing.updated_at = datetime.now(timezone.utc)
        db.commit(); db.refresh(existing)
        rubric = _serialize_rubric(existing, db)
        db.close()
        return rubric
    normalized_entries = _normalize_and_validate_entries(db, data.criteria)
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
    for pos, entry in enumerate(normalized_entries):
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
    rubric = _serialize_rubric(orm, db)
    db.close()
    return rubric


def update_rubric(rubric_id: str, data: RubricUpdate) -> Optional[Rubric]:
    db = SessionLocal()
    orm = db.query(RubricORM).filter(RubricORM.id == rubric_id).first()
    if not orm:
        db.close(); return None
    # In-place upsert: apply updates regardless of published state
    if data.description is not None:
        orm.description = data.description
    if data.criteria is not None:
        # Capture existing weights by criterion_id to preserve when incoming weight is omitted
        existing_weights_map = {rc.criterion_id: float(rc.weight) for rc in orm.criteria_assoc}
        normalized_entries = _normalize_and_validate_entries(db, data.criteria, existing_weights=existing_weights_map)
        # Clear existing association rows explicitly so flush removes them
        for existing in list(orm.criteria_assoc):
            db.delete(existing)
        orm.criteria_assoc = []
        db.flush()  # ensure deletes are applied before inserts to avoid unique constraint
        for pos, entry in enumerate(normalized_entries):
            orm.criteria_assoc.append(RubricCriterionORM(
                id=str(uuid.uuid4()),
                rubric_id=orm.id,
                criterion_id=entry.criteriaId,
                position=pos,
                weight=entry.weight,
            ))
    # association rows already updated
    orm.updated_at = datetime.now(timezone.utc)
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
        db.close(); return _serialize_rubric(orm)
    orm.published = True
    orm.published_at = datetime.now(timezone.utc)
    orm.updated_at = datetime.now(timezone.utc)
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
