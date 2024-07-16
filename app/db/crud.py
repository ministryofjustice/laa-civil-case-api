from sqlalchemy.orm import Session

from . import models, schemas


def get_case(db: Session, case_id: int):
    return db.query(models.Case).filter(models.Case.id == case_id).first()

def create_case(db: Session, case: schemas.CaseCreate):
    case = models.Case(email=case.email)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case