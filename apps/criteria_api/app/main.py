
from fastapi import FastAPI
from app.routes import criteria
from app.utils.db import Base, engine
from app.models import criteria_orm

app = FastAPI()

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app.include_router(criteria.router, prefix="/criteria", tags=["criteria"])

@app.get("/")
def root():
    return {"message": "Criteria API is running"}
