import os
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.utils.db import SessionLocal
from app.models.criteria_orm import CriteriaORM

client = TestClient(app)


def _create_criterion(name="Cw1"):
    db = SessionLocal()
    cid = str(uuid.uuid4())
    c = CriteriaORM(id=cid, name=name, description=name+" desc", definition="def")
    db.add(c)
    db.commit()
    db.close()
    return cid


def test_create_rubric_missing_weights_get_defaults():
    c1 = _create_criterion("W1")
    resp = client.post("/rubrics/", json={
        "name": f"Rubric {uuid.uuid4().hex[:6]}",
        "description": "desc",
        "criteria": [
            {"criteriaId": c1}
        ]
    })
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["criteria"][0]["weight"] is not None


def test_invalid_zero_weight_when_disallowed():
    c1 = _create_criterion("W2")
    resp = client.post("/rubrics/", json={
        "name": f"Rubric {uuid.uuid4().hex[:6]}",
        "description": "desc",
        "criteria": [
            {"criteriaId": c1, "weight": 0}
        ]
    })
    assert resp.status_code == 422
    assert resp.json()["detail"]["error"] == "INVALID_WEIGHT"


def test_duplicate_criteria_rejected_new_schema():
    c1 = _create_criterion("W3")
    resp = client.post("/rubrics/", json={
        "name": f"Rubric {uuid.uuid4().hex[:6]}",
        "description": "desc",
        "criteria": [
            {"criteriaId": c1, "weight": 1},
            {"criteriaId": c1, "weight": 2},
        ]
    })
    assert resp.status_code == 422
    assert resp.json()["detail"]["error"] == "DUPLICATE_CRITERIA"


def test_over_max_weight():
    c1 = _create_criterion("W4")
    resp = client.post("/rubrics/", json={
        "name": f"Rubric {uuid.uuid4().hex[:6]}",
        "description": "desc",
        "criteria": [
            {"criteriaId": c1, "weight": 1_000_001}
        ]
    })
    assert resp.status_code == 422
    assert resp.json()["detail"]["error"] == "WEIGHT_TOO_LARGE"


def test_update_changes_weight_before_publish():
    c1 = _create_criterion("W5")
    name = f"Rubric {uuid.uuid4().hex[:6]}"
    create = client.post("/rubrics/", json={
        "name": name,
        "description": "desc",
        "criteria": [
            {"criteriaId": c1, "weight": 2}
        ]
    })
    rid = create.json()["id"]
    upd = client.put(f"/rubrics/{rid}", json={
        "criteria": [
            {"criteriaId": c1, "weight": 3}
        ]
    })
    assert upd.status_code == 200
    assert upd.json()["criteria"][0]["weight"] == 3.0


def test_publish_blocks_weight_change():
    c1 = _create_criterion("W6")
    name = f"Rubric {uuid.uuid4().hex[:6]}"
    create = client.post("/rubrics/", json={
        "name": name,
        "description": "desc",
        "criteria": [
            {"criteriaId": c1, "weight": 2}
        ]
    })
    rid = create.json()["id"]
    pub = client.post(f"/rubrics/{rid}/publish")
    assert pub.status_code == 200
    upd = client.put(f"/rubrics/{rid}", json={
        "criteria": [
            {"criteriaId": c1, "weight": 4}
        ]
    })
    assert upd.status_code == 409
