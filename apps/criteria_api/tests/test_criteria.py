import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Criteria API is running"

def test_create_and_crud_criteria(monkeypatch):
    # Mock CosmosDB for isolated test
    from app.services import criteria_service
    class DummyContainer:
        def __init__(self):
            self.items = {}
        def read_all_items(self):
            return self.items.values()
        def create_item(self, body):
            self.items[body["id"]] = body
        def read_item(self, item, partition_key):
            return self.items[item]
        def replace_item(self, item, body):
            self.items[item] = body
        def delete_item(self, item, partition_key):
            del self.items[item]
    dummy = DummyContainer()
    monkeypatch.setattr(criteria_service, "get_container", lambda: dummy)

    # Baseline count (seed may have inserted rows)
    baseline = client.get("/criteria/").json()
    base_len = len(baseline)
    # Create
    resp = client.post("/criteria/", json={"name": "A", "description": "desc", "definition": "def"})
    assert resp.status_code == 201
    data = resp.json()
    cid = data["id"]
    # List should increase by 1
    resp = client.get("/criteria/")
    assert resp.status_code == 200
    assert len(resp.json()) == base_len + 1
    # Get
    resp = client.get(f"/criteria/{cid}")
    assert resp.status_code == 200
    # Update
    resp = client.put(f"/criteria/{cid}", json={"description": "desc2"})
    assert resp.status_code == 200
    assert resp.json()["description"] == "desc2"
    # Delete
    resp = client.delete(f"/criteria/{cid}")
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    # Not found after delete
    resp = client.get(f"/criteria/{cid}")
    assert resp.status_code == 404


def test_update_with_blank_id_creates_new(monkeypatch):
    # Ensure the service container stub exists for backward compatibility
    from app.services import criteria_service

    class DummyContainer:
        def __init__(self):
            self.items = {}
        def read_all_items(self):
            return self.items.values()
        def create_item(self, body):
            self.items[body["id"]] = body
        def read_item(self, item, partition_key):
            return self.items[item]
        def replace_item(self, item, body):
            self.items[item] = body
        def delete_item(self, item, partition_key):
            del self.items[item]

    dummy = DummyContainer()
    monkeypatch.setattr(criteria_service, "get_container", lambda: dummy)

    # Baseline count
    baseline = client.get("/criteria/").json()
    base_len = len(baseline)

    # PUT with a blank-like id "undefined" should create a new criteria
    payload = {"name": "New via PUT", "description": "desc", "definition": "def"}
    resp = client.put("/criteria/undefined", json=payload)
    assert resp.status_code == 200
    created = resp.json()
    assert created.get("id")
    assert created["name"] == payload["name"]

    # Count should increase by 1
    resp = client.get("/criteria/")
    assert resp.status_code == 200
    assert len(resp.json()) == base_len + 1
