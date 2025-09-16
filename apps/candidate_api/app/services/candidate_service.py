import uuid
import logging
from datetime import datetime
from typing import List, Optional
from app.models.candidate import Candidate, CandidateCreate
from shared_utils.cosmos import candidate_repository, CosmosRepository

logger = logging.getLogger(__name__)

_candidate_repo: CosmosRepository | None = None

def _get_repo() -> CosmosRepository:
    global _candidate_repo
    if _candidate_repo is None:
        _candidate_repo = candidate_repository()
    return _candidate_repo


def list_candidates() -> List[Candidate]:
    r = _get_repo()
    # Simple query to list all
    items = r.query("SELECT * FROM c")
    logger.debug("Fetched %d candidates", len(items))
    return [Candidate(**item) for item in items]


def get_candidate(candidate_id: str) -> Optional[Candidate]:
    r = _get_repo()
    item = r.get(candidate_id)
    if not item:
        logger.info("Candidate not found: %s", candidate_id)
        return None
    logger.debug("Retrieved candidate %s", candidate_id)
    return Candidate(**item)


def create_candidate(data: CandidateCreate) -> Candidate:
    r = _get_repo()
    normalized = data.name.strip().lower()
    # uniqueness check
    existing = r.query("SELECT TOP 1 * FROM c WHERE c.nameNormalized = @n", parameters=[{"name": "@n", "value": normalized}])
    if existing:
        logger.warning("Attempt to create duplicate candidate name=%s", data.name)
        raise ValueError("Candidate with that name already exists")
    new_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    item = {
        "id": new_id,
        "name": data.name,
        "nameNormalized": normalized,
        "description": data.description,
        "createdAt": now,
        "updatedAt": now,
    }
    r.create(item)
    logger.info("Created candidate id=%s name=%s", new_id, data.name)
    return Candidate(**item)
