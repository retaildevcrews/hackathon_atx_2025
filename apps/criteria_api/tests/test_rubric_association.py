import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.utils.db import SessionLocal
from app.models.criteria_orm import CriteriaORM
from app.models.rubric_criterion_orm import RubricCriterionORM

client = TestClient(app)


def _create_criterion(name="C1"):
    db = SessionLocal()
    cid = str(uuid.uuid4())
    c = CriteriaORM(id=cid, name=name, description=name+" desc", definition="def")
    db.add(c)
    db.commit()
    db.close()
    return cid


def test_create_rubric_creates_assoc_rows():
    c1 = _create_criterion("CritA")
    c2 = _create_criterion("CritB")
    resp = client.post("/rubrics/", json={
        "name": f"Rubric {uuid.uuid4().hex[:6]}",
        "description": "desc",
        "criteria": [
            {"criteriaId": c1, "weight": 0.5},
            {"criteriaId": c2, "weight": 0.5},
        ]
    })
    assert resp.status_code == 201, resp.text
    rid = resp.json()["id"]
    db = SessionLocal()
    rows = db.query(RubricCriterionORM).filter(RubricCriterionORM.rubric_id == rid).order_by(RubricCriterionORM.position).all()
    assert len(rows) == 2
    assert rows[0].position == 0 and rows[1].position == 1
    db.close()


def test_update_reorders_positions():
    c1 = _create_criterion("CritC")
    c2 = _create_criterion("CritD")
    name = f"Rubric {uuid.uuid4().hex[:6]}"
    resp = client.post("/rubrics/", json={
        "name": name,
        "description": "desc",
        "criteria": [
            {"criteriaId": c1, "weight": 0.4},
            {"criteriaId": c2, "weight": 0.6},
        ]
    })
    rid = resp.json()["id"]
    # reorder
    resp2 = client.put(f"/rubrics/{rid}", json={
        "criteria": [
            {"criteriaId": c2, "weight": 0.6},
            {"criteriaId": c1, "weight": 0.4},
        ]
    })
    assert resp2.status_code == 200
    db = SessionLocal()
    rows = db.query(RubricCriterionORM).filter(RubricCriterionORM.rubric_id == rid).order_by(RubricCriterionORM.position).all()
    assert rows[0].criterion_id == c2 and rows[0].position == 0
    assert rows[1].criterion_id == c1 and rows[1].position == 1
    db.close()


def test_publish_then_update_fails():
    c1 = _create_criterion("CritE")
    name = f"Rubric {uuid.uuid4().hex[:6]}"
    resp = client.post("/rubrics/", json={
        "name": name,
        "description": "desc",
        "criteria": [
            {"criteriaId": c1, "weight": 1.0},
        ]
    })
    rid = resp.json()["id"]
    pub = client.post(f"/rubrics/{rid}/publish")
    assert pub.status_code == 200
    upd = client.put(f"/rubrics/{rid}", json={"description": "new"})
    assert upd.status_code == 409


def test_delete_draft_cascades():
    c1 = _create_criterion("CritF")
    name = f"Rubric {uuid.uuid4().hex[:6]}"
    resp = client.post("/rubrics/", json={
        "name": name,
        "description": "desc",
        "criteria": [
            {"criteriaId": c1, "weight": 1.0},
        ]
    })
    rid = resp.json()["id"]
    delr = client.delete(f"/rubrics/{rid}")
    assert delr.status_code == 204
    db = SessionLocal()
    rows = db.query(RubricCriterionORM).filter(RubricCriterionORM.rubric_id == rid).all()
    assert len(rows) == 0
    db.close()


def test_duplicate_criterion_rejected():
    c1 = _create_criterion("CritG")
    name = f"Rubric {uuid.uuid4().hex[:6]}"
    resp = client.post("/rubrics/", json={
        "name": name,
        "description": "desc",
        "criteria": [
            {"criteriaId": c1, "weight": 0.5},
            {"criteriaId": c1, "weight": 0.5},
        ]
    })
    # Now returns structured validation error 422
    assert resp.status_code == 422
