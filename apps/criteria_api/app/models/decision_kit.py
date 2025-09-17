from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime


class DecisionKitCandidateRef(BaseModel):
    id: str
    candidateId: str = Field(..., description="Candidate UUID")
    candidateName: str
    position: int


class DecisionKitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rubricId: str
    candidateIds: List[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str):
        if not v or len(v) < 3 or len(v) > 60:
            raise ValueError("name length 3-60 required")
        import re
        if not re.match(r"^[A-Za-z0-9 _-]+$", v):
            raise ValueError("invalid characters in name")
        return v


class DecisionKitUpdateCandidates(BaseModel):
    candidateIds: List[str]


class DecisionKit(BaseModel):
    id: str
    name: str
    description: Optional[str]
    rubricId: str
    rubricVersion: str
    rubricPublished: bool
    status: str
    evaluation_id: Optional[str] = None
    candidates: List[DecisionKitCandidateRef] = Field(default_factory=list)
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=True)
