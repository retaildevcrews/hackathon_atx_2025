
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import criteria, rubrics, decision_kits, candidates
from app.utils.db import Base, engine
from app.models import criteria_orm  # ensure import side effects
from app.models import rubric_orm  # ensure rubric table
from app.models import rubric_criterion_orm  # ensure assoc table
from app.models import decision_kit_orm  # ensure decision kit tables
from app.models import candidate_orm  # ensure candidate table
from sqlalchemy import text
from app.seed.seed_data import seed
from app.config import settings

app = FastAPI()

# CORS (hackathon-permissive; tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _migrate_legacy_rubric_schema():
    """If existing SQLite rubrics table still has legacy criteria_json column, rebuild it without that column."""
    with engine.connect() as conn:
        try:
            rows = conn.execute(text("PRAGMA table_info(rubrics)")).fetchall()
        except Exception:
            return  # table might not exist yet
        if not rows:
            return
        has_legacy = any(r[1] == 'criteria_json' for r in rows)
        if not has_legacy:
            return
        # Rebuild table
        conn.execute(text("BEGIN TRANSACTION"))
        conn.execute(text("CREATE TABLE rubrics_new (\n            id TEXT PRIMARY KEY,\n            name_normalized TEXT NOT NULL,\n            name_original TEXT NOT NULL,\n            version TEXT NOT NULL,\n            description TEXT NOT NULL,\n            published BOOLEAN NOT NULL,\n            published_at DATETIME NULL,\n            created_at DATETIME NOT NULL,\n            updated_at DATETIME NOT NULL\n        )"))
        conn.execute(text("INSERT INTO rubrics_new (id,name_normalized,name_original,version,description,published,published_at,created_at,updated_at) SELECT id,name_normalized,name_original,version,description,published,published_at,created_at,updated_at FROM rubrics"))
        conn.execute(text("DROP TABLE rubrics"))
        conn.execute(text("ALTER TABLE rubrics_new RENAME TO rubrics"))
        # Recreate index that SQLAlchemy would have made for name_normalized (if desired)
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_rubrics_name_normalized ON rubrics (name_normalized)"))
        conn.execute(text("COMMIT"))


_migrate_legacy_rubric_schema()
Base.metadata.create_all(bind=engine)

# Seed sample data only if empty
seed()

app.include_router(criteria.router, prefix="/criteria", tags=["criteria"])
app.include_router(rubrics.router, prefix="/rubrics", tags=["rubrics"])
app.include_router(decision_kits.router, prefix="/decision-kits", tags=["decision_kits"])
app.include_router(candidates.router, prefix="/candidates", tags=["candidates"]) 

@app.get("/")
def root():
    return {"message": "Criteria API is running"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/settings")
def get_settings():
    # Expose only safe, non-sensitive runtime configuration for clients
    return {
        "rubricWeightMin": settings.RUBRIC_WEIGHT_MIN,
        "rubricWeightMax": settings.RUBRIC_WEIGHT_MAX,
        "rubricWeightStep": settings.RUBRIC_WEIGHT_STEP,
        "defaultRubricWeight": settings.DEFAULT_RUBRIC_WEIGHT,
        "allowZeroWeight": settings.ALLOW_ZERO_WEIGHT,
    }
