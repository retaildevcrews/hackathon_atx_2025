from __future__ import annotations

from pydantic import BaseModel, Field


class InvokeRequest(BaseModel):
    prompt: str = Field(..., description="Prompt text to evaluate or process")


class InvokeResponse(BaseModel):
    output: str
    model: str | None = None
    stub: bool | None = None
