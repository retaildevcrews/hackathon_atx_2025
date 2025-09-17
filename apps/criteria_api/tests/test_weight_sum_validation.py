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


def test_create_rubric_requires_weights_sum_to_one():
    c1 = _create_criterion("W1")
    c2 = _create_criterion("W2")
    name = f"Rubric {uuid.uuid4().hex[:6]}"
    # Sum 0.9 -> invalid
    r_bad = client.post("/rubrics/", json={
        "name": name,
        "description": "d",
        "criteria": [
            {"criteriaId": c1, "weight": 0.40},
            {"criteriaId": c2, "weight": 0.50},
        ]
    })
    assert r_bad.status_code == 422, r_bad.text
    detail = r_bad.json().get("detail")
    if isinstance(detail, dict):
        assert detail.get("error") == "INVALID_WEIGHT_SUM"

    # Sum 1.0 -> valid
    r_ok = client.post("/rubrics/", json={
        "name": f"{name}-ok",
        "description": "d",
        "criteria": [
            {"criteriaId": c1, "weight": 0.40},
            {"criteriaId": c2, "weight": 0.60},
        ]
    })
    assert r_ok.status_code == 201, r_ok.text


def test_update_rubric_requires_weights_sum_to_one():
    c1 = _create_criterion("UW1")
    c2 = _create_criterion("UW2")
    name = f"Rubric {uuid.uuid4().hex[:6]}"
    # Create valid rubric first
    r = client.post("/rubrics/", json={
        "name": name,
        "description": "d",
        "criteria": [
            {"criteriaId": c1, "weight": 0.50},
            {"criteriaId": c2, "weight": 0.50},
        ]
    })
    assert r.status_code == 201, r.text
    rid = r.json()["id"]

    # Update with invalid sum 0.95 -> should 422
    u_bad = client.put(f"/rubrics/{rid}", json={
        "criteria": [
            {"criteriaId": c1, "weight": 0.40},
            {"criteriaId": c2, "weight": 0.55},
        ]
    })
    assert u_bad.status_code == 422, u_bad.text
    detail = u_bad.json().get("detail")
    if isinstance(detail, dict):
        assert detail.get("error") == "INVALID_WEIGHT_SUM"

    # Update with valid sum 1.0 -> should 200
    u_ok = client.put(f"/rubrics/{rid}", json={
        "criteria": [
            {"criteriaId": c1, "weight": 0.45},
            {"criteriaId": c2, "weight": 0.55},
        ]
    })
    assert u_ok.status_code == 200, u_ok.text
