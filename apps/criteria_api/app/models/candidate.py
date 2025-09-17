from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import re

_NAME_PATTERN = re.compile(r"^[A-Za-z0-9 _.-]+$")


class CandidateCreate(BaseModel):
    """Payload for creating a candidate.
    """
    name: str = Field(..., description="Display name (2-80 chars, limited charset)")
    description: Optional[str] = Field(None, description="Optional description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str):  # noqa: D401 - simple validation
        if not v or len(v) < 2 or len(v) > 80:
            raise ValueError("name length 2-80 required")
        if not _NAME_PATTERN.match(v):
            raise ValueError("invalid characters in name")
        return v


class Candidate(BaseModel):
    """Candidate response model.
    """
    id: str
    name: str
    nameNormalized: str
    description: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=False)


class CandidateMaterial(BaseModel):
    id: str
    candidateId: str
    filename: str
    contentType: str
    sizeBytes: int
    blobPath: str
    createdAt: datetime

    model_config = ConfigDict(from_attributes=False)


class CandidateMaterialList(BaseModel):
    items: List[CandidateMaterial]
    total: int
