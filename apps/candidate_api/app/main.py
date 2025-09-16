from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Early import to ensure .env variables are loaded before shared_utils (cosmos/blob) modules resolve env vars.
from app import config  # noqa: F401
from app.routes import candidates

app = FastAPI()

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
