from sqlalchemy import Column, String, Text
from app.utils.db import Base

class CriteriaORM(Base):
    __tablename__ = "criteria"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    definition = Column(Text, nullable=False)
