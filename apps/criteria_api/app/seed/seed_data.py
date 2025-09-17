import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.criteria_orm import CriteriaORM
from app.models.rubric_orm import RubricORM
from app.models.rubric_criterion_orm import RubricCriterionORM
from app.models.candidate_orm import CandidateORM
from app.models.decision_kit_orm import DecisionKitORM, DecisionKitCandidateORM


TV_RUBRIC_NAME = "TV Evaluation"
TV_RUBRIC_DESCRIPTION = "Sample television evaluation rubric (seed data)."

_ROWS = [
    {
        "name": "Picture Quality",
        "weight": 0.20,
        "description": "Measures resolution, contrast, color accuracy, and HDR support.",
        "levels": [
            (5, "Excellent", "OLED/QLED, 4K/8K, HDR10+, Dolby Vision"),
            (4, "Good", "High-res LED, good contrast"),
            (3, "Fair", "Standard HD, decent colors"),
            (2, "Poor", "Washed out or uneven"),
            (1, "Very Poor", "Blurry or pixelated"),
        ],
    },
    {
        "name": "Sound Quality",
        "weight": 0.10,
        "description": "Evaluates speaker clarity, bass, and surround sound support.",
        "levels": [
            (5, "Excellent", "Dolby Atmos, rich sound"),
            (4, "Good", "Clear, good volume"),
            (3, "Fair", "Average, lacks depth"),
            (2, "Poor", "Tinny or muffled"),
            (1, "Very Poor", "Distorted or weak"),
        ],
    },
    {
        "name": "Smart App Support",
        "weight": 0.15,
        "description": "Assesses streaming app availability and smart interface performance.",
        "levels": [
            (5, "Excellent", "Full ecosystem, fast UI"),
            (4, "Good", "Most major apps, responsive"),
            (3, "Fair", "Limited apps, some lag"),
            (2, "Poor", "Few apps, slow UI"),
            (1, "Very Poor", "No smart features"),
        ],
    },
    {
        "name": "Gaming Performance",
        "weight": 0.15,
        "description": "Evaluates input lag, refresh rate, HDMI 2.1, and responsiveness.",
        "levels": [
            (5, "Excellent", "Low lag, 120Hz, VRR"),
            (4, "Good", "Good response, 60Hz"),
            (3, "Fair", "Moderate lag"),
            (2, "Poor", "Noticeable lag"),
            (1, "Very Poor", "Not suitable for gaming"),
        ],
    },
    {
        "name": "Movie Watching Experience",
        "weight": 0.10,
        "description": "Focuses on cinematic modes, ambient lighting, and motion handling.",
        "levels": [
            (5, "Excellent", "Cinematic modes, immersive sound"),
            (4, "Good", "Good picture modes"),
            (3, "Fair", "Basic settings"),
            (2, "Poor", "Poor contrast/sound"),
            (1, "Very Poor", "Unwatchable quality"),
        ],
    },
    {
        "name": "Ease of Use",
        "weight": 0.10,
        "description": "Considers interface intuitiveness, remote design, and setup.",
        "levels": [
            (5, "Excellent", "Intuitive UI, voice control"),
            (4, "Good", "Simple UI, decent remote"),
            (3, "Fair", "Some learning curve"),
            (2, "Poor", "Confusing interface"),
            (1, "Very Poor", "Frustrating to use"),
        ],
    },
    {
        "name": "Family-Friendly Features",
        "weight": 0.10,
        "description": "Includes parental controls, kid-safe modes, and multi-user profiles.",
        "levels": [
            (5, "Excellent", "Full controls, profiles, kid modes"),
            (4, "Good", "Some controls, basic profiles"),
            (3, "Fair", "Limited features"),
            (2, "Poor", "Few safety options"),
            (1, "Very Poor", "No family support"),
        ],
    },
    {
        "name": "Design & Aesthetics",
        "weight": 0.05,
        "description": "Evaluates how well the TV fits into a shared space visually.",
        "levels": [
            (5, "Excellent", "Sleek, minimal bezel"),
            (4, "Good", "Modern, acceptable look"),
            (3, "Fair", "Bulky but okay"),
            (2, "Poor", "Outdated design"),
            (1, "Very Poor", "Ugly or intrusive"),
        ],
    },
    {
        "name": "Price/Value",
        "weight": 0.05,
        "description": "Assesses value for features and performance relative to cost.",
        "levels": [
            (5, "Excellent", "Excellent value"),
            (4, "Good", "Good balance"),
            (3, "Fair", "Fair for budget"),
            (2, "Poor", "Overpriced"),
            (1, "Very Poor", "Not worth it"),
        ],
    },
]


def seed():
    """Seed criteria, rubric, candidates, and a sample decision kit if empty.

    This function is idempotent: if a rubric already exists it assumes prior seeding
    (and skips creating duplicates). Additional entities are only created when absent.
    """
    db: Session = SessionLocal()
    try:
        has_rubric = db.query(RubricORM).first() is not None
        if has_rubric:
            # Still ensure at least one decision kit and a few candidates exist.
            if db.query(CandidateORM).count() == 0:
                for name in ["Alpha", "Beta", "Gamma"]:
                    display = f"Candidate {name}"
                    db.add(CandidateORM(
                        id=str(uuid.uuid4()),
                        name=display,
                        name_normalized=display.lower().strip(),
                        description=f"Seeded candidate {name}",
                    ))
                db.commit()
            if db.query(DecisionKitORM).first() is None:
                rubric_row = db.query(RubricORM).first()
                cand_rows = db.query(CandidateORM).all()
                kit_id = str(uuid.uuid4())
                kit = DecisionKitORM(
                    id=kit_id,
                    name_normalized="sample decision kit",
                    name_original="Sample Decision Kit",
                    description="Seeded decision kit linking sample candidates",
                    rubric_id=rubric_row.id,
                    rubric_version=rubric_row.version,
                    rubric_published=rubric_row.published,
                )
                db.add(kit); db.flush()
                for pos, c in enumerate(cand_rows):
                    db.add(DecisionKitCandidateORM(
                        id=str(uuid.uuid4()),
                        decision_kit_id=kit.id,
                        candidate_id=c.id,
                        position=pos,
                    ))
                db.commit()
            return
        criteria_records = []
        rubric_entries = []
        for row in _ROWS:
            cid = str(uuid.uuid4())
            # Compose a plain text / markdown style definition instead of JSON
            levels_lines = [
                f"{sc} - {label}: {desc}" for sc, label, desc in row["levels"]
            ]
            definition_text = (
                f"Summary: {row['description']}\n" +
                "Levels:\n" +
                "\n".join(levels_lines)
            )
            criteria_records.append(
                CriteriaORM(
                    id=cid,
                    name=row["name"],
                    description=row["description"],
                    definition=definition_text,
                )
            )
            rubric_entries.append({"criteriaId": cid, "weight": row["weight"]})

        for c in criteria_records:
            db.add(c)
        db.commit()

        rubric_id = str(uuid.uuid4())
        rubric = RubricORM(
            id=rubric_id,
            name_normalized=TV_RUBRIC_NAME.lower(),
            name_original=TV_RUBRIC_NAME,
            version="1.0.0",
            description=TV_RUBRIC_DESCRIPTION,
            published=True,
            published_at=datetime.now(timezone.utc),
        )
        db.add(rubric)
        db.commit()
        # create association rows
        for pos, entry in enumerate(rubric_entries):
            db.add(RubricCriterionORM(
                id=str(uuid.uuid4()),
                rubric_id=rubric_id,
                criterion_id=entry["criteriaId"],
                position=pos,
                weight=entry["weight"],
            ))
        db.commit()

        # Seed Candidates
        candidate_ids = []
        for name in ["Alpha", "Beta", "Gamma"]:
            cid = str(uuid.uuid4())
            candidate_ids.append(cid)
            display = f"Candidate {name}"
            db.add(CandidateORM(
                id=cid,
                name=display,
                name_normalized=display.lower().strip(),
                description=f"Seeded candidate {name}",
            ))
        db.commit()

        # Seed Decision Kit referencing all candidates
        kit_id = str(uuid.uuid4())
        kit = DecisionKitORM(
            id=kit_id,
            name_normalized="sample decision kit",
            name_original="Sample Decision Kit",
            description="Seeded decision kit linking sample candidates",
            rubric_id=rubric_id,
            rubric_version=rubric.version,
            rubric_published=rubric.published,
        )
        db.add(kit); db.flush()
        for pos, cid in enumerate(candidate_ids):
            cand = db.query(CandidateORM).filter(CandidateORM.id == cid).first()
            db.add(DecisionKitCandidateORM(
                id=str(uuid.uuid4()),
                decision_kit_id=kit.id,
                candidate_id=cid,
                position=pos,
            ))
        db.commit()
    finally:
        db.close()
