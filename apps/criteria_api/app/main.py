
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import criteria, rubrics
from app.utils.db import Base, engine
from app.models import criteria_orm  # ensure import side effects
from app.models import rubric_orm  # ensure rubric table

app = FastAPI()

# CORS (hackathon-permissive; tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app.include_router(criteria.router, prefix="/criteria", tags=["criteria"])
app.include_router(rubrics.router, prefix="/rubrics", tags=["rubrics"])

@app.get("/")
def root():
    return {"message": "Criteria API is running"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
