from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime


class RubricCriteriaEntryBase(BaseModel):
    criteriaId: str = Field(..., description="Referenced criteria UUID")
    weight: Optional[float] = Field(
        None,
        description="Criterion weight; optional on create/update (default applied if omitted)."
    )


class RubricCriteriaEntryCreate(RubricCriteriaEntryBase):
    pass


class RubricCriteriaEntry(RubricCriteriaEntryBase):
    # In responses weight is always present
    weight: float = Field(..., description="Criterion weight (always present in responses)")
    # Optional enrichment metadata
    name: str | None = Field(None, description="Criteria name (enriched)")
    description: str | None = Field(None, description="Criteria description (enriched)")
    definition: str | None = Field(None, description="Criteria definition (enriched)")


class RubricBase(BaseModel):
    name: str
    description: str
    criteria: List[RubricCriteriaEntryCreate] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str):
        if not v or len(v) < 3 or len(v) > 60:
            raise ValueError("name length 3-60 required")
        import re
        if not re.match(r"^[A-Za-z0-9 _-]+$", v):
            raise ValueError("invalid characters in name")
        return v


class RubricCreate(RubricBase):
    pass


class RubricUpdate(BaseModel):
    description: Optional[str] = None
    criteria: Optional[List[RubricCriteriaEntryCreate]] = None


class Rubric(RubricBase):
    id: str
    version: str
    published: bool
    publishedAt: Optional[datetime]
    createdAt: datetime
    updatedAt: datetime

    # Override criteria type for responses (weight required)
    criteria: List[RubricCriteriaEntry]

    model_config = ConfigDict(from_attributes=True)
