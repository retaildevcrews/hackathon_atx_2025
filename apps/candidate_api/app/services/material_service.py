import uuid
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import UploadFile
from app.models.candidate import CandidateMaterial, CandidateMaterialList
from shared_utils.cosmos import material_repository, CosmosRepository
from shared_utils.blob import get_blob_client
from app.config import get_settings, get_max_file_size_bytes

logger = logging.getLogger(__name__)

_materials_repo: CosmosRepository | None = None

def _get_repo() -> CosmosRepository:
    global _materials_repo
    if _materials_repo is None:
        _materials_repo = material_repository()
    return _materials_repo


def list_materials(candidate_id: str) -> CandidateMaterialList:
    r = _get_repo()
    items = r.query("SELECT * FROM c WHERE c.candidateId = @cid ORDER BY c.createdAt DESC", parameters=[{"name": "@cid", "value": candidate_id}])
    mats = [CandidateMaterial(**item) for item in items]
    logger.debug("Fetched %d materials for candidate %s", len(mats), candidate_id)
    return CandidateMaterialList(items=mats, total=len(mats))


def create_material(candidate_id: str, file: UploadFile) -> CandidateMaterial:
    settings = get_settings()
    max_size = get_max_file_size_bytes()

    data = file.file.read()
    size = len(data)
    if size == 0:
        logger.warning("Empty material upload candidate=%s filename=%s", candidate_id, file.filename)
        raise ValueError("Empty file")
    if size > max_size:
        logger.warning("Oversized material upload candidate=%s filename=%s size=%d", candidate_id, file.filename, size)
        raise ValueError("File exceeds max size")
    # MIME validation (prefix match)
    allowed = settings.allowed_mime_prefix_list()
    if not any(file.content_type.startswith(p) for p in allowed):
        logger.warning("Disallowed MIME type candidate=%s filename=%s mime=%s", candidate_id, file.filename, file.content_type)
        raise ValueError("Disallowed MIME type")

    r = _get_repo()
    new_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    blob_rel_path = f"candidates/{candidate_id}/{new_id}_{file.filename}"
    # Upload to blob (or disabled fallback)
    blob_client = get_blob_client()
    blob_url = blob_client.upload_bytes(data, blob_rel_path, content_type=file.content_type or "application/octet-stream")
    item = {
        "id": new_id,
        "candidateId": candidate_id,
        "filename": file.filename,
        "contentType": file.content_type or "application/octet-stream",
        "sizeBytes": size,
    "blobPath": blob_url,
        "createdAt": now,
    }
    r.create(item)
    logger.info("Created material id=%s candidate=%s filename=%s size=%d", new_id, candidate_id, file.filename, size)
    return CandidateMaterial(**item)


def get_material(candidate_id: str, material_id: str) -> Optional[CandidateMaterial]:
    r = _get_repo()
    results = r.query("SELECT * FROM c WHERE c.candidateId = @cid AND c.id = @mid", parameters=[{"name": "@cid", "value": candidate_id}, {"name": "@mid", "value": material_id}])
    if not results:
        logger.info("Material not found candidate=%s material=%s", candidate_id, material_id)
        return None
    return CandidateMaterial(**results[0])


def delete_material(candidate_id: str, material_id: str) -> bool:
    # Simple delete by composite search then remove by id
    r = _get_repo()
    results = r.query("SELECT * FROM c WHERE c.candidateId = @cid AND c.id = @mid", parameters=[{"name": "@cid", "value": candidate_id}, {"name": "@mid", "value": material_id}])
    if not results:
        logger.info("Delete material not found candidate=%s material=%s", candidate_id, material_id)
        return False
    # For now partition key is candidateId, so deletion needs correct PK; repository uses /candidateId
    r.container.delete_item(item=material_id, partition_key=candidate_id)
    logger.info("Deleted material id=%s candidate=%s", material_id, candidate_id)
    return True
