from __future__ import annotations

import logging
from fastapi import FastAPI

from config import get_settings
from routes import invoke as invoke_route

logger = logging.getLogger(__name__)

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.get("/version")
async def version() -> dict[str, str]:
    return {"name": settings.app_name, "version": settings.app_version}


app.include_router(invoke_route.router)


@app.get("/healthz")
async def health() -> dict[str, str]:
    return {"status": "ok"}
