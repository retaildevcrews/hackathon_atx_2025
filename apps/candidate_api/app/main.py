from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Early import to ensure .env variables are loaded before shared_utils (cosmos/blob) modules resolve env vars.
from app import config  # noqa: F401
from app.routes import candidates

app = FastAPI(
    title="Candidate API",
    description="""Manage candidates and their uploaded materials.\n\n"
                "This service provides endpoints to create candidates, list them, and manage related document uploads."
                " Uses Cosmos DB (candidates + materials) and optional Azure Blob Storage (fallback when unset).""",
    version="0.1.0",
    contact={
        "name": "Platform Team",
        "url": "https://example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "candidates",
            "description": "Candidate CRUD and material upload operations.",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidates.router, prefix="/candidates", tags=["candidates"])

@app.get("/")
async def root():
    return {"message": "Candidate API running"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
