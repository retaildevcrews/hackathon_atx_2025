from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import re

_NAME_PATTERN = re.compile(r"^[A-Za-z0-9 _.-]+$")


class CandidateCreate(BaseModel):
    """Payload for creating a candidate.

    Candidate must always be created within a decision kit context. Name uniqueness
    is enforced per decision kit (case-insensitive, normalized).
    """
    name: str = Field(..., description="Display name (2-80 chars, limited charset)")
    description: Optional[str] = Field(None, description="Optional description")
    decisionKitId: str = Field(..., description="Decision kit to which this candidate is added")

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


class CandidateUpdate(BaseModel):
    """Payload for updating a candidate's metadata.

    Follows same validation constraints as create. decisionKitId optional for future
    reassignment support; currently ignored by backend logic (association retained).
    """
    name: str = Field(..., description="Updated display name")
    description: Optional[str] = Field(None, description="Updated description")
    decisionKitId: Optional[str] = Field(None, description="(Reserved) decision kit context for validation")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str):  # noqa: D401 - simple validation
        if not v or len(v) < 2 or len(v) > 80:
            raise ValueError("name length 2-80 required")
        if not _NAME_PATTERN.match(v):
            raise ValueError("invalid characters in name")
        return v


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
