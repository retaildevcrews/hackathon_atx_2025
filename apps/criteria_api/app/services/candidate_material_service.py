import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.utils.db import SessionLocal
from app.models.candidate_orm import CandidateMaterialORM
from app.models.candidate import CandidateMaterial, CandidateMaterialList


# For now we do not integrate Azure Blob; we keep a pseudo path so contract stays similar.
def _pseudo_blob_path(candidate_id: str, material_id: str, filename: str) -> str:
    return f"candidates/{candidate_id}/{material_id}_{filename}"


def _serialize(orm: CandidateMaterialORM) -> CandidateMaterial:
    return CandidateMaterial(
        id=orm.id,
        candidateId=orm.candidate_id,
        filename=orm.filename,
        contentType=orm.content_type,
        sizeBytes=orm.size_bytes,
        blobPath=orm.blob_path,
        createdAt=orm.created_at,
    )


def list_materials(candidate_id: str) -> CandidateMaterialList:
    db: Session = SessionLocal()
    rows = (
        db.query(CandidateMaterialORM)
        .filter(CandidateMaterialORM.candidate_id == candidate_id)
        .order_by(CandidateMaterialORM.created_at.desc())
        .all()
    )
    items = [_serialize(r) for r in rows]
    total = len(items)
    db.close()
    return CandidateMaterialList(items=items, total=total)


def create_material(candidate_id: str, file: UploadFile) -> CandidateMaterial:
    data = file.file.read()
    size = len(data)
    if size == 0:
        raise ValueError("Empty file")
    # Basic size guard (10MB default like legacy). Could be moved to settings if needed.
    max_size = 10 * 1024 * 1024
    if size > max_size:
        raise ValueError("File exceeds max size")
    material_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    blob_path = _pseudo_blob_path(candidate_id, material_id, file.filename)
    db = SessionLocal()
    orm = CandidateMaterialORM(
        id=material_id,
        candidate_id=candidate_id,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=size,
        blob_path=blob_path,
        created_at=now,
    )
    db.add(orm)
    db.commit(); db.refresh(orm)
    out = _serialize(orm)
    db.close()
    return out


def get_material(candidate_id: str, material_id: str) -> Optional[CandidateMaterial]:
    db = SessionLocal()
    orm = (
        db.query(CandidateMaterialORM)
        .filter(
            CandidateMaterialORM.candidate_id == candidate_id,
            CandidateMaterialORM.id == material_id,
        )
        .first()
    )
    if not orm:
        db.close(); return None
    out = _serialize(orm)
    db.close()
    return out


def delete_material(candidate_id: str, material_id: str) -> bool:
    db = SessionLocal()
    orm = (
        db.query(CandidateMaterialORM)
        .filter(
            CandidateMaterialORM.candidate_id == candidate_id,
            CandidateMaterialORM.id == material_id,
        )
        .first()
    )
    if not orm:
        db.close(); return False
    db.delete(orm)
    db.commit()
    db.close()
    return True
