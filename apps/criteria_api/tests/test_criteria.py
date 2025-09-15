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

    # Create
    resp = client.post("/criteria/", json={"name": "A", "description": "desc", "definition": "def"})
    assert resp.status_code == 201
    data = resp.json()
    cid = data["id"]
    # List
    resp = client.get("/criteria/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
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
