from sqlalchemy import Column, String
from app.utils.db import Base


class CandidateORM(Base):
    """Simple candidate entity for Decision Kits.
    In a real system this might live in a separate service; for MVP we localize it.
    """
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
