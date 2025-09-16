import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.utils.db import SessionLocal
from app.models.candidate_orm import CandidateORM
from app.models.rubric_orm import RubricORM


client = TestClient(app)


def _ensure_candidates(n=3):
    db = SessionLocal()
    try:
        existing = db.query(CandidateORM).all()
        if len(existing) >= n:
            return [c.id for c in existing[:n]]
        ids = []
        for i in range(n - len(existing)):
            cid = str(uuid.uuid4())
            db.add(CandidateORM(id=cid, name=f"Candidate {i}"))
            ids.append(cid)
        db.commit()
        allc = db.query(CandidateORM).all()
        return [c.id for c in allc[:n]]
    finally:
        db.close()


def _get_any_rubric_id():
    db = SessionLocal(); rid=None
    try:
        r = db.query(RubricORM).first()
        if r:
            rid = r.id
    finally:
        db.close()
    return rid


def test_create_decision_kit_success():
    rid = _get_any_rubric_id()
    candidate_ids = _ensure_candidates(2)
    unique_name = f"My Kit {uuid.uuid4().hex[:6]}"
    resp = client.post("/decision-kits/", json={
        "name": unique_name,
        "description": "Test kit",
        "rubricId": rid,
        "candidateIds": candidate_ids,
    })
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["name"] == unique_name
    assert len(data["candidates"]) == 2
    assert data["candidates"][0]["position"] == 0


def test_duplicate_name_conflict():
    rid = _get_any_rubric_id()
    candidate_ids = _ensure_candidates(1)
    base_name = f"Unique Kit {uuid.uuid4().hex[:6]}"
    payload = {
        "name": base_name,
        "description": None,
        "rubricId": rid,
        "candidateIds": candidate_ids,
    }
    r1 = client.post("/decision-kits/", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/decision-kits/", json=payload)
    assert r2.status_code == 409


def test_invalid_candidate_id():
    rid = _get_any_rubric_id()
    bad_id = str(uuid.uuid4())
    resp = client.post("/decision-kits/", json={
        "name": "Bad Kit",
        "description": None,
        "rubricId": rid,
        "candidateIds": [bad_id],
    })
    assert resp.status_code == 422


def test_update_candidates_reorder_and_remove():
    rid = _get_any_rubric_id()
    cids = _ensure_candidates(3)
    reorder_name = f"Reorder Kit {uuid.uuid4().hex[:6]}"
    create = client.post("/decision-kits/", json={
        "name": reorder_name,
        "description": None,
        "rubricId": rid,
        "candidateIds": cids,
    })
    assert create.status_code == 201
    kit_id = create.json()["id"]
    # reorder (swap first two) and remove last
    new_order = [cids[1], cids[0]]
    upd = client.put(f"/decision-kits/{kit_id}/candidates", json={"candidateIds": new_order})
    assert upd.status_code == 200, upd.text
    data = upd.json()
    assert [c["candidateId"] for c in data["candidates"]] == new_order
    assert len(data["candidates"]) == 2


def test_delete_decision_kit():
    rid = _get_any_rubric_id()
    cids = _ensure_candidates(1)
    temp_name = f"Temp Kit {uuid.uuid4().hex[:6]}"
    create = client.post("/decision-kits/", json={
        "name": temp_name,
        "description": None,
        "rubricId": rid,
        "candidateIds": cids,
    })
    kit_id = create.json()["id"]
    d = client.delete(f"/decision-kits/{kit_id}")
    assert d.status_code == 204
    g = client.get(f"/decision-kits/{kit_id}")
    assert g.status_code == 404


def test_update_nonexistent_kit():
    resp = client.put(f"/decision-kits/{uuid.uuid4()}/candidates", json={"candidateIds": []})
    assert resp.status_code == 404
