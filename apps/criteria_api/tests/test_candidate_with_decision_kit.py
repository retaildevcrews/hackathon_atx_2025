import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.utils.db import SessionLocal
from app.models.decision_kit_orm import DecisionKitORM
from app.models.rubric_orm import RubricORM
from app.models.candidate_orm import CandidateORM

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


def _ensure_decision_kit():
    """Create a minimal decision kit (no candidates) if none exists, return its id."""
    db = SessionLocal(); kit_id=None
    try:
        existing = db.query(DecisionKitORM).first()
        if existing:
            return existing.id
        # Need a rubric
        rid = _get_any_rubric_id()
        if not rid:
            raise RuntimeError("No rubric available for test")
        kit_id = str(uuid.uuid4())
        kit = DecisionKitORM(
            id=kit_id,
            name_normalized=f"test kit {kit_id}".lower(),
            name_original=f"Test Kit {kit_id[:8]}",
            description="Test kit for candidate attach",
            rubric_id=rid,
            rubric_version="1.0.0",
            rubric_published=True,
        )
        db.add(kit); db.commit()
        return kit_id
    finally:
        db.close()


def test_create_candidate_with_decision_kit_attachment():
    kit_id = _ensure_decision_kit()
    candidate_name = f"Attach Candidate {uuid.uuid4().hex[:6]}"
    resp = client.post("/candidates/", json={
        "name": candidate_name,
        "description": "Attached via creation",
        "decisionKitId": kit_id,
    })
    assert resp.status_code == 201, resp.text
    cand_data = resp.json()
    # Fetch the kit and ensure candidate appears in list
    kit_resp = client.get(f"/decision-kits/{kit_id}")
    assert kit_resp.status_code == 200, kit_resp.text
    kit = kit_resp.json()
    found = [c for c in kit["candidates"] if c["candidateId"] == cand_data["id"]]
    assert found, "Candidate not associated with decision kit"
    # Position should be last index
    assert found[0]["position"] == len(kit["candidates"]) - 1


def test_create_candidate_with_invalid_decision_kit():
    bad_id = str(uuid.uuid4())
    resp = client.post("/candidates/", json={
        "name": f"BadKitCandidate {uuid.uuid4().hex[:4]}",
        "decisionKitId": bad_id,
    })
    assert resp.status_code == 400
    assert "invalid decision kit" in resp.text.lower()
