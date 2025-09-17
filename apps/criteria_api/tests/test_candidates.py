import io
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_candidate_success():
    payload = {"name": "Jane Doe", "description": "Senior Engineer"}
    r = client.post("/candidates/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == payload["name"]
    assert data["nameNormalized"] == payload["name"].lower()
    assert data["description"] == payload["description"]
    assert "id" in data


def test_create_candidate_duplicate_name():
    payload = {"name": "Duplicate Person"}
    r1 = client.post("/candidates/", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/candidates/", json=payload)
    assert r2.status_code == 400
    assert "exists" in r2.json()["detail"].lower()


def test_get_candidate_not_found():
    r = client.get("/candidates/does-not-exist")
    assert r.status_code == 404


def test_list_candidates_ordering():
    # create two; ensure most recent first by createdAt desc (implementation uses created_at desc)
    n1 = client.post("/candidates/", json={"name": "Order Test A"}).json()
    n2 = client.post("/candidates/", json={"name": "Order Test B"}).json()
    r = client.get("/candidates/")
    assert r.status_code == 200
    items = r.json()
    ids = [i["id"] for i in items]
    # B should appear before A (most recent first)
    assert ids.index(n2["id"]) < ids.index(n1["id"])


def test_material_upload_and_list_and_delete():
    cand = client.post("/candidates/", json={"name": "Material Owner"}).json()
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
    cand = client.post("/candidates/", json={"name": "Empty File Owner"}).json()
    files = {"file": ("empty.txt", b"", "text/plain")}
    r_up = client.post(f"/candidates/{cand['id']}/materials", files=files)
    assert r_up.status_code == 400
    assert "empty" in r_up.json()["detail"].lower()


def test_material_upload_oversize_rejected():
    cand = client.post("/candidates/", json={"name": "Big File Owner"}).json()
    # create >10MB in memory (10MB + 1 byte)
    big = b"a" * (10 * 1024 * 1024 + 1)
    files = {"file": ("big.bin", big, "application/octet-stream")}
    r_up = client.post(f"/candidates/{cand['id']}/materials", files=files)
    assert r_up.status_code == 400
    assert "exceeds" in r_up.json()["detail"].lower()
