import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.utils.db import SessionLocal
from app.models.criteria_orm import CriteriaORM

client = TestClient(app)


def _create_criterion(name: str = "Crit") -> str:
    db = SessionLocal()
    try:
        cid = str(uuid.uuid4())
        c = CriteriaORM(id=cid, name=name, description=f"{name} desc", definition="def")
        db.add(c)
        db.commit()
        return cid
    finally:
        db.close()


def test_weight_preserved_when_omitted_on_update():
    # Create criterion and rubric with a valid decimal weight
    crit_id = _create_criterion("PreserveW")
    rubric_name = f"Rubric {uuid.uuid4().hex[:6]}"
    create = client.post("/rubrics/", json={
        "name": rubric_name,
        "description": "desc",
        "criteria": [
            {"criteriaId": crit_id, "weight": 0.35}
        ]
    })
    assert create.status_code == 201, create.text
    rid = create.json()["id"]
    assert abs(create.json()["criteria"][0]["weight"] - 0.35) < 1e-9

    # Update omitting weight should preserve the existing weight (not default to 1.0)
    update = client.put(f"/rubrics/{rid}", json={
        "criteria": [
            {"criteriaId": crit_id}
        ]
    })
    assert update.status_code == 200, update.text
    assert abs(update.json()["criteria"][0]["weight"] - 0.35) < 1e-9


def test_weight_must_be_in_005_increments():
    crit_id = _create_criterion("StepBad")
    resp = client.post("/rubrics/", json={
        "name": f"Rubric {uuid.uuid4().hex[:6]}",
        "description": "d",
        "criteria": [
            {"criteriaId": crit_id, "weight": 0.12}
        ]
    })
    assert resp.status_code == 422, resp.text
    detail = resp.json().get("detail")
    # On 422 we surface the structured error
    if isinstance(detail, dict):
        assert detail.get("error") == "INVALID_WEIGHT"


def test_weight_range_enforced():
    crit_id = _create_criterion("RangeBad")
    # Below 0.05
    r1 = client.post("/rubrics/", json={
        "name": f"Rubric {uuid.uuid4().hex[:6]}",
        "description": "d",
        "criteria": [
            {"criteriaId": crit_id, "weight": 0.04}
        ]
    })
    assert r1.status_code == 422
    # Above 1.0
    r2 = client.post("/rubrics/", json={
        "name": f"Rubric {uuid.uuid4().hex[:6]}",
        "description": "d",
        "criteria": [
            {"criteriaId": crit_id, "weight": 1.05}
        ]
    })
    assert r2.status_code == 422
    
    # Valid boundary values
    r3 = client.post("/rubrics/", json={
        "name": f"Rubric {uuid.uuid4().hex[:6]}",
        "description": "d",
        "criteria": [
            {"criteriaId": crit_id, "weight": 0.05}
        ]
    })
    assert r3.status_code == 201, r3.text
    r4 = client.post("/rubrics/", json={
        "name": f"Rubric {uuid.uuid4().hex[:6]}",
        "description": "d",
        "criteria": [
            {"criteriaId": crit_id, "weight": 1.00}
        ]
    })
    assert r4.status_code == 201, r4.text
