import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class DummyRepo:
    def __init__(self, partition_key="/id"):
        self.partition_key = partition_key
        self.items = {}
    def query(self, query: str, parameters=None):
        # very naive filtering for tests
        if "nameNormalized" in query:
            target = None
            for p in parameters or []:
                if p["name"] == "@n":
                    target = p["value"]
            return [v for v in self.items.values() if v.get("nameNormalized") == target] if target else []
        if "candidateId" in query and "id" in query:
            cid = mid = None
            for p in parameters or []:
                if p["name"] == "@cid":
                    cid = p["value"]
                if p["name"] == "@mid":
                    mid = p["value"]
            return [v for v in self.items.values() if v.get("candidateId") == cid and v.get("id") == mid]
        if "candidateId" in query:
            cid = None
            for p in parameters or []:
                if p["name"] == "@cid":
                    cid = p["value"]
            items = [v for v in self.items.values() if v.get("candidateId") == cid]
            # order by createdAt desc simulated
            return sorted(items, key=lambda x: x.get("createdAt"), reverse=True)
        return list(self.items.values())
    def create(self, item):
        self.items[item["id"]] = item
        return item
    def get(self, item_id, partition_value=None):
        return self.items.get(item_id)
    def delete(self, item_id, partition_value=None):
        if item_id in self.items:
            del self.items[item_id]

class DummyBlob:
    def upload_bytes(self, data: bytes, blob_path: str, container=None, content_type=None):
        return f"disabled://{blob_path}"  # mimic fallback

@pytest.fixture(autouse=True)
def patch_repos(monkeypatch):
    # Patch repository factories
    from shared_utils import cosmos as cosmos_mod
    from shared_utils import blob as blob_mod
    cand_repo = DummyRepo(partition_key="/id")
    mat_repo = DummyRepo(partition_key="/candidateId")
    monkeypatch.setattr(cosmos_mod, "candidate_repository", lambda: cand_repo)
    monkeypatch.setattr(cosmos_mod, "material_repository", lambda: mat_repo)
    dummy_blob = DummyBlob()
    monkeypatch.setattr(blob_mod, "get_blob_client", lambda: dummy_blob)
    yield


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["message"].startswith("Candidate API")


def test_candidate_crud_and_materials():
    # Create candidate
    resp = client.post("/candidates/", json={"name": "Alice", "description": "Desc"})
    assert resp.status_code == 201
    cand = resp.json()
    cid = cand["id"]

    # Duplicate should fail
    resp_dup = client.post("/candidates/", json={"name": "Alice", "description": "Other"})
    assert resp_dup.status_code == 400

    # Get candidate
    resp_get = client.get(f"/candidates/{cid}")
    assert resp_get.status_code == 200

    # List candidates
    resp_list = client.get("/candidates/")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) == 1

    # Upload material (valid)
    file_content = b"Sample resume text"
    resp_mat = client.post(
        f"/candidates/{cid}/materials",
        files={"file": ("resume.txt", io.BytesIO(file_content), "text/plain")},
    )
    assert resp_mat.status_code == 201
    mat = resp_mat.json()
    mid = mat["id"]
    assert mat["blobPath"].startswith("disabled://candidates/")

    # List materials
    resp_mats = client.get(f"/candidates/{cid}/materials")
    assert resp_mats.status_code == 200
    mats = resp_mats.json()
    assert mats["total"] == 1

    # Get material
    resp_get_mat = client.get(f"/candidates/{cid}/materials/{mid}")
    assert resp_get_mat.status_code == 200

    # Delete material
    resp_del = client.delete(f"/candidates/{cid}/materials/{mid}")
    assert resp_del.status_code == 200
    assert resp_del.json()["success"] is True

    # Material now gone
    resp_get_mat2 = client.get(f"/candidates/{cid}/materials/{mid}")
    assert resp_get_mat2.status_code == 404

    # Candidate still there
    resp_get2 = client.get(f"/candidates/{cid}")
    assert resp_get2.status_code == 200


def test_material_validation_errors():
    # Create candidate
    resp = client.post("/candidates/", json={"name": "Bob", "description": "Desc"})
    assert resp.status_code == 201
    cid = resp.json()["id"]

    # Empty file
    resp_empty = client.post(
        f"/candidates/{cid}/materials",
        files={"file": ("empty.txt", io.BytesIO(b""), "text/plain")},
    )
    assert resp_empty.status_code == 400

    # Disallowed mime
    resp_bad_mime = client.post(
        f"/candidates/{cid}/materials",
        files={"file": ("file.bin", io.BytesIO(b"data"), "application/octet-stream")},
    )
    assert resp_bad_mime.status_code == 400


def test_material_endpoints_missing_candidate():
    missing_id = "non-existent-id"
    # List materials should 404
    r_list = client.get(f"/candidates/{missing_id}/materials")
    assert r_list.status_code == 404
    # Upload should 404
    r_up = client.post(
        f"/candidates/{missing_id}/materials",
        files={"file": ("resume.txt", io.BytesIO(b"abc"), "text/plain")},
    )
    assert r_up.status_code == 404
    # Get material should 404
    r_get = client.get(f"/candidates/{missing_id}/materials/some-material")
    assert r_get.status_code == 404
    # Delete material should 404
    r_del = client.delete(f"/candidates/{missing_id}/materials/some-material")
    assert r_del.status_code == 404
