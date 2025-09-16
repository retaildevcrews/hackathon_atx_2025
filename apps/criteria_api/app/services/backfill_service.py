"""Backfill logic for migrating legacy rubric.criteria_json to rubric_criteria association rows.

Runs at startup before the app begins serving requests. Controlled via env flags:
  KEEP_CRITERIA_JSON (default true) - retain legacy JSON content (else cleared)
  DISABLE_JSON_CRITERIA_BACKFILL (default false) - skip migration if true
"""
import os
import uuid
import json
from typing import List
from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.rubric_orm import RubricORM
from app.models.rubric_criterion_orm import RubricCriterionORM


KEEP_CRITERIA_JSON = os.getenv("KEEP_CRITERIA_JSON", "true").lower() == "true"
DISABLE_BACKFILL = os.getenv("DISABLE_JSON_CRITERIA_BACKFILL", "false").lower() == "true"


def _parse_legacy(json_text: str) -> List[dict]:
    try:
        data = json.loads(json_text or "[]")
        if isinstance(data, list):
            # expect list of {criteriaId, weight?}
            filtered = []
            seen = set()
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                cid = entry.get("criteriaId") or entry.get("criteria_id")
                if not cid or cid in seen:
                    continue
                seen.add(cid)
                filtered.append({
                    "criteriaId": cid,
                    "weight": entry.get("weight")
                })
            return filtered
    except Exception:
        return []
    return []


def run_backfill(logger=print):
    if DISABLE_BACKFILL:
        logger("[backfill] Skipped (DISABLE_JSON_CRITERIA_BACKFILL=true)")
        return
    db: Session = SessionLocal()
    migrated = 0
    already = 0
    skipped_err = 0
    total = 0
    max_criteria = 0
    try:
        rubrics: List[RubricORM] = db.query(RubricORM).all()
        total = len(rubrics)
        # inventory
        for r in rubrics:
            legacy_entries = _parse_legacy(r.criteria_json)
            max_criteria = max(max_criteria, len(legacy_entries) if legacy_entries else len(r.criteria_assoc or []))
        logger(f"[backfill] inventory rubrics={total} maxCriteriaPerRubric={max_criteria}")
        for r in rubrics:
            if r.criteria_assoc and len(r.criteria_assoc) > 0:
                already += 1
                continue
            legacy_entries = _parse_legacy(r.criteria_json)
            if not legacy_entries:
                already += 1
                continue
            try:
                # shape validation: ensure each entry has criteriaId key
                bad = [e for e in legacy_entries if 'criteriaId' not in e]
                if bad:
                    skipped_err += 1
                    logger(f"[backfill] malformed criteria entries for rubric {r.id}; skipping")
                    continue
                for pos, entry in enumerate(legacy_entries):
                    rc = RubricCriterionORM(
                        id=str(uuid.uuid4()),
                        rubric_id=r.id,
                        criterion_id=entry["criteriaId"],
                        position=pos,
                        weight=entry.get("weight"),
                    )
                    db.add(rc)
                if not KEEP_CRITERIA_JSON:
                    r.criteria_json = "[]"  # clear legacy
                db.commit()
                migrated += 1
            except Exception as e:
                db.rollback()
                skipped_err += 1
                logger(f"[backfill] Error migrating rubric {r.id}: {e}")
        logger(f"[backfill] summary total={total} migrated={migrated} already_modern={already} errors={skipped_err}")
    finally:
        db.close()
