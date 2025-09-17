import uuid
from azure.storage.blob import BlobServiceClient, ContentSettings
from datetime import datetime, timezone
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
import os
import logging
import mimetypes

from app.utils.db import SessionLocal
from app.models.candidate_orm import CandidateMaterialORM
from app.models.candidate import CandidateMaterial, CandidateMaterialList


# For now we do not integrate Azure Blob; we keep a pseudo path so contract stays similar.
def _pseudo_blob_path(candidate_id: str, material_id: str, filename: str) -> str:
    return f"candidates/{candidate_id}/{material_id}_{filename}"

def _pseudo_save_blob(
    blob_path: str,
    data: bytes,
    candidate_id: str,
    material_id: str,
) -> None:
    """Upload file bytes to Azure Blob Storage if configured.

    Environment variables:
      - AZURE_STORAGE_CONNECTION_STRING: Azure Storage connection string (preferred)
      - STORAGE_CONN_STRING: legacy alternate name
      - CANDIDATE_MATERIALS_CONTAINER: target container name (defaults to 'raw-docs')

    If the connection string is not configured, this function will log a warning and
    return without raising to preserve existing behavior for local development.
    """
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING") or os.getenv("STORAGE_CONN_STRING")
    container = os.getenv("CANDIDATE_MATERIALS_CONTAINER", "raw-docs")
    if not conn_str:
        logging.warning("AZURE_STORAGE_CONNECTION_STRING not set; skipping blob upload for %s", blob_path)
        return

    try:
        service = BlobServiceClient.from_connection_string(conn_str)
        blob_client = service.get_blob_client(container=container, blob=blob_path)
        content_type, _ = mimetypes.guess_type(blob_path)
        content_settings = ContentSettings(content_type=content_type or "application/octet-stream")
        # include candidate and material ids as blob metadata
        metadata = {"candidate_id": candidate_id, "material_id": material_id}
        # Upload the data (overwrite any existing blob at this path)
        blob_client.upload_blob(data, overwrite=True, content_settings=content_settings, metadata=metadata)
        logging.debug("Uploaded blob to container=%s path=%s", container, blob_path)
    except Exception as exc:
        logging.exception("Failed to upload blob to Azure Storage for %s", blob_path, exc_info=exc)
        raise



def _pseudo_delete_blob(blob_path: str, candidate_id: str, material_id: str) -> None:
    """Delete a blob from Azure Blob Storage if configured.

    Mirrors behavior of _pseudo_save_blob: if no connection string is set,
    log a warning and return without raising to preserve local development flow.
    """
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING") or os.getenv("STORAGE_CONN_STRING")
    container = os.getenv("CANDIDATE_MATERIALS_CONTAINER", "raw-docs")
    if not conn_str:
        logging.warning("AZURE_STORAGE_CONNECTION_STRING not set; skipping blob delete for %s", blob_path)
        return

    try:
        service = BlobServiceClient.from_connection_string(conn_str)
        blob_client = service.get_blob_client(container=container, blob=blob_path)
        blob_client.delete_blob()
        logging.debug("Deleted blob from container=%s path=%s", container, blob_path)
    except Exception as exc:
        logging.exception("Failed to delete blob from Azure Storage for %s", blob_path, exc_info=exc)
        raise


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
    _pseudo_save_blob(blob_path, data)
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

    # attempt to delete the corresponding blob in storage
    _blob_path = _pseudo_blob_path(candidate_id, material_id, orm.filename)
    _pseudo_delete_blob(_blob_path, candidate_id, material_id)
    return True
