from sqlalchemy import Column, String, Text, Boolean, DateTime
from datetime import datetime
import json
from app.utils.db import Base


class RubricORM(Base):
    __tablename__ = "rubrics"

    id = Column(String, primary_key=True, index=True)
    name_normalized = Column(String, index=True, nullable=False)  # lowercased for uniqueness check
    name_original = Column(String, nullable=False)
    version = Column(String, nullable=False, default="1.0.0")
    description = Column(Text, nullable=False)
    criteria_json = Column(Text, nullable=False, default="[]")
    published = Column(Boolean, default=False, nullable=False)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def set_criteria(self, criteria_list):
        self.criteria_json = json.dumps(criteria_list or [])
        self.updated_at = datetime.utcnow()

    def get_criteria(self):
        try:
            return json.loads(self.criteria_json or "[]")
        except json.JSONDecodeError:
            return []
