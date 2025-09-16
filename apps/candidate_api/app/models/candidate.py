from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import re

NAME_PATTERN = re.compile(r"^[A-Za-z0-9 _.-]+$")

class CandidateCreate(BaseModel):
    name: str
    description: Optional[str] = None

    @validator("name")
    def validate_name(cls, v: str):
        if not v or len(v) < 2 or len(v) > 80:
            raise ValueError("name length 2-80 required")
        if not NAME_PATTERN.match(v):
            raise ValueError("invalid characters in name")
        return v

class Candidate(BaseModel):
    id: str
    name: str
    nameNormalized: str
    description: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

class CandidateMaterial(BaseModel):
    id: str
    candidateId: str
    filename: str
    contentType: str
    sizeBytes: int
    blobPath: str
    createdAt: datetime

class CandidateMaterialList(BaseModel):
    items: List[CandidateMaterial]
    total: int
