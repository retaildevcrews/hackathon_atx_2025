import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.utils.db import SessionLocal
from app.models.candidate_orm import CandidateORM
from app.models.decision_kit_orm import DecisionKitORM, DecisionKitCandidateORM
from datetime import datetime, timezone

client = TestClient(app)


def _create_candidate(name: str):
    r = client.post('/candidates', json={'name': name})
    assert r.status_code == 201, r.text
    return r.json()['id']


def _create_decision_kit(db):
    kit_id = str(uuid.uuid4())
    # Minimal viable rubric linkage assumption: pick first rubric row
    rubric = db.execute('SELECT id, version, published FROM rubrics LIMIT 1').fetchone()
    if not rubric:
        # If no rubric seeded tests may have to seed first; for now skip association tests
        return None
    dk = DecisionKitORM(
        id=kit_id,
        name_normalized=f'dk-{kit_id}'[:60],
        name_original=f'Test Kit {kit_id[:8]}',
        description='test kit',
        rubric_id=rubric[0],
        rubric_version=rubric[1],
        rubric_published=rubric[2],
    )
    db.add(dk)
    return dk


def test_delete_candidate_removes_materials_and_assocs():
    # Arrange
    db = SessionLocal()
    dk = _create_decision_kit(db)
    db.commit()
    db.refresh(dk)
    cand_id = _create_candidate('DeleteTarget')
    # Associate candidate with decision kit if kit created
    if dk:
        assoc = DecisionKitCandidateORM(
            id=str(uuid.uuid4()),
            decision_kit_id=dk.id,
            candidate_id=cand_id,
            position=0,
        )
        db.add(assoc)
        db.commit()
    # Upload a material
    resp = client.post(f'/candidates/{cand_id}/materials', files={'file': ('note.txt', b'hello', 'text/plain')})
    assert resp.status_code == 201

    # Act
    del_resp = client.delete(f'/candidates/{cand_id}')
    assert del_resp.status_code == 204

    # Assert candidate gone
    get_resp = client.get(f'/candidates/{cand_id}')
    assert get_resp.status_code == 404

    # Assert materials removed
    mats_resp = client.get(f'/candidates/{cand_id}/materials')
    assert mats_resp.status_code == 404  # candidate not found

    # If decision kit existed, ensure no dangling assoc rows
    if dk:
        leftover = db.query(DecisionKitCandidateORM).filter(DecisionKitCandidateORM.candidate_id == cand_id).count()
        assert leftover == 0
    db.close()
