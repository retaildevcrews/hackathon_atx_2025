import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services import rubric_service

client = TestClient(app)


def test_update_rubric_adds_new_criteria_when_missing_id():
    # Create a rubric first
    create_payload = {
        "name": "Web Quality Rubric",
        "description": "Initial",
        "criteria": []
    }
    resp = client.post("/rubrics/", json=create_payload)
    assert resp.status_code == 201
    rubric = resp.json()
    rid = rubric["id"]

    # Update with one existing criterion missing criteriaId but with fields to create it
    update_payload = {
        "description": "Updated",
        "criteria": [
            {
                # criteriaId omitted intentionally
                "name": "Accessibility",
                "description": "WCAG basics",
                "definition": "Perceivable, Operable, Understandable, Robust",
                "weight": 0.5
            }
        ]
    }

    resp = client.put(f"/rubrics/{rid}", json=update_payload)
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["description"] == "Updated"
    assert len(updated["criteria"]) == 1
    entry = updated["criteria"][0]
    # The API should enrich with a generated criteriaId and echo weight
    assert "criteriaId" in entry and entry["criteriaId"]
    assert entry["weight"] == 0.5
    # Enrichment fields should be present (best effort, may be null if not fetched)
    assert entry.get("name") in ("Accessibility", None)
    assert isinstance(entry.get("description"), (str, type(None)))
    assert isinstance(entry.get("definition"), (str, type(None)))
