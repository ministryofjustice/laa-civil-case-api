from sqlalchemy.orm import Session

from . import models, schemas


def get_case(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_case(db: Session, user: schemas.UserCreate):
    case = models.User(email=user.email)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case