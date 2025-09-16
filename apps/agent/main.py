from __future__ import annotations

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routes import invoke as invoke_route
from routes import evaluation as evaluation_route

logger = logging.getLogger(__name__)

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)

# NOTE: Permissive CORS for initial development. DO NOT leave allow_origins=['*'] in production.
# Update to explicit origins, e.g. ["https://your-frontend.example.com"].
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: tighten in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/version")
async def version() -> dict[str, str]:
    return {"name": settings.app_name, "version": settings.app_version}


app.include_router(invoke_route.router)
app.include_router(evaluation_route.router)


@app.get("/healthz")
async def health() -> dict[str, str]:
    return {"status": "ok"}
