from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class RubricCriteriaEntry(BaseModel):
    criteriaId: str = Field(..., description="Referenced criteria UUID")
    weight: Optional[float] = Field(None, ge=0, le=1, description="Optional weight 0-1")


class RubricBase(BaseModel):
    name: str
    description: str
    criteria: List[RubricCriteriaEntry] = Field(default_factory=list)

    @validator("name")
    def validate_name(cls, v: str):
        if not v or len(v) < 3 or len(v) > 60:
            raise ValueError("name length 3-60 required")
        # Simple pattern check (alnum, space, dash, underscore)
        import re
        if not re.match(r"^[A-Za-z0-9 _-]+$", v):
            raise ValueError("invalid characters in name")
        return v


class RubricCreate(RubricBase):
    pass


class RubricUpdate(BaseModel):
    description: Optional[str]
    criteria: Optional[List[RubricCriteriaEntry]]


class Rubric(RubricBase):
    id: str
    version: str
    published: bool
    publishedAt: Optional[datetime]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True
