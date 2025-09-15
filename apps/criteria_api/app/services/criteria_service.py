
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.criteria import Criteria, CriteriaCreate, CriteriaUpdate
from app.models.criteria_orm import CriteriaORM
from app.utils.db import SessionLocal

def list_criteria() -> List[Criteria]:
    db: Session = SessionLocal()
    items = db.query(CriteriaORM).all()
    db.close()
    return [Criteria(**item.__dict__) for item in items]

def get_criteria_by_id(criteria_id: str) -> Optional[Criteria]:
    db: Session = SessionLocal()
    item = db.query(CriteriaORM).filter(CriteriaORM.id == criteria_id).first()
    db.close()
    if not item:
        return None
    return Criteria(**item.__dict__)

def create_criteria(data: CriteriaCreate) -> Criteria:
    db: Session = SessionLocal()
    new_id = str(uuid.uuid4())
    item = CriteriaORM(id=new_id, **data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    db.close()
    return Criteria(**item.__dict__)

def update_criteria(criteria_id: str, data: CriteriaUpdate) -> Optional[Criteria]:
    db: Session = SessionLocal()
    item = db.query(CriteriaORM).filter(CriteriaORM.id == criteria_id).first()
    if not item:
        db.close()
        return None
    for field, value in data.dict(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    db.close()
    return Criteria(**item.__dict__)

def delete_criteria(criteria_id: str) -> bool:
    db: Session = SessionLocal()
    item = db.query(CriteriaORM).filter(CriteriaORM.id == criteria_id).first()
    if not item:
        db.close()
        return False
    db.delete(item)
    db.commit()
    db.close()
    return True
