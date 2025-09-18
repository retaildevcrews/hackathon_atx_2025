import io
import json
from fastapi.testclient import TestClient
from app.main import app
from app.utils.db import SessionLocal
from app.models.rubric_orm import RubricORM
from app.models.decision_kit_orm import DecisionKitORM
import uuid

client = TestClient(app)


def _get_any_rubric_id():
    db = SessionLocal(); rid=None
    try:
        r = db.query(RubricORM).first()
        if r:
            rid = r.id
    finally:
        db.close()
    return rid


def _new_decision_kit():
    """Create a fresh decision kit each time to isolate candidate uniqueness constraints.

    Tests previously reused the first decision kit which caused candidate name collisions
    (e.g., multiple tests attempting to create "Jane Doe"). We instead generate a unique
    kit per test using UUIDs so candidate names can repeat safely across tests while still
    ensuring uniqueness within a single kit is enforced.
    """
    db = SessionLocal()
    try:
        rid = _get_any_rubric_id()
        dk = DecisionKitORM(
            id=str(uuid.uuid4()),
            name_normalized=f"test-kit-{uuid.uuid4()}",
            name_original="Test Kit",
            description="Per-test kit for candidate tests",
            rubric_id=rid,
            rubric_version="1.0.0",
            rubric_published=True,
        )
        db.add(dk)
        db.commit()
        return dk.id
    finally:
        db.close()


def test_create_candidate_success():
    kit_id = _new_decision_kit()
    payload = {"name": "Jane Doe", "description": "Senior Engineer", "decisionKitId": kit_id}
    r = client.post("/candidates/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == payload["name"]
    assert data["nameNormalized"] == payload["name"].lower()
    assert data["description"] == payload["description"]
    assert "id" in data


def test_create_candidate_duplicate_name():
    kit_id = _new_decision_kit()
    payload = {"name": "Duplicate Person", "decisionKitId": kit_id}
    r1 = client.post("/candidates/", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/candidates/", json=payload)
    assert r2.status_code == 400
    assert "exists" in r2.json()["detail"].lower()


def test_get_candidate_not_found():
    r = client.get("/candidates/does-not-exist")
    assert r.status_code == 404


def test_list_candidates_ordering():
    kit_id = _new_decision_kit()
    # create two; ensure most recent first by createdAt desc (implementation uses created_at desc)
    n1 = client.post("/candidates/", json={"name": "Order Test A", "decisionKitId": kit_id}).json()
    n2 = client.post("/candidates/", json={"name": "Order Test B", "decisionKitId": kit_id}).json()
    r = client.get("/candidates/")
    assert r.status_code == 200
    items = r.json()
    ids = [i["id"] for i in items]
    # B should appear before A (most recent first)
    assert ids.index(n2["id"]) < ids.index(n1["id"])


def test_material_upload_and_list_and_delete():
    kit_id = _new_decision_kit()
    cand = client.post("/candidates/", json={"name": "Material Owner", "decisionKitId": kit_id}).json()
    file_content = b"hello world" * 100
    files = {"file": ("test.txt", file_content, "text/plain")}
    r_up = client.post(f"/candidates/{cand['id']}/materials", files=files)
    assert r_up.status_code == 201, r_up.text
    mat = r_up.json()
    assert mat["filename"] == "test.txt"
    # list
    r_list = client.get(f"/candidates/{cand['id']}/materials")
    assert r_list.status_code == 200
    lst = r_list.json()
    assert lst["total"] == 1
    # get single
    r_get = client.get(f"/candidates/{cand['id']}/materials/{mat['id']}")
    assert r_get.status_code == 200
    # delete
    r_del = client.delete(f"/candidates/{cand['id']}/materials/{mat['id']}")
    assert r_del.status_code == 200
    # ensure gone
    r_get2 = client.get(f"/candidates/{cand['id']}/materials/{mat['id']}")
    assert r_get2.status_code == 404


def test_material_upload_empty_file_rejected():
    kit_id = _new_decision_kit()
    cand = client.post("/candidates/", json={"name": "Empty File Owner", "decisionKitId": kit_id}).json()
    files = {"file": ("empty.txt", b"", "text/plain")}
    r_up = client.post(f"/candidates/{cand['id']}/materials", files=files)
    assert r_up.status_code == 400
    assert "empty" in r_up.json()["detail"].lower()


def test_material_upload_oversize_rejected():
    kit_id = _new_decision_kit()
    cand = client.post("/candidates/", json={"name": "Big File Owner", "decisionKitId": kit_id}).json()
    # create >10MB in memory (10MB + 1 byte)
    big = b"a" * (10 * 1024 * 1024 + 1)
    files = {"file": ("big.bin", big, "application/octet-stream")}
    r_up = client.post(f"/candidates/{cand['id']}/materials", files=files)
    assert r_up.status_code == 400
    assert "exceeds" in r_up.json()["detail"].lower()
