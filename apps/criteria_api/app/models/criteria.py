from pydantic import BaseModel, Field
from typing import Optional

class Criteria(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique identifier")
    name: str
    description: str
    definition: str

class CriteriaCreate(BaseModel):
    name: str
    description: str
    definition: str

class CriteriaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[str] = None
