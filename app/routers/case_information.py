from fastapi import APIRouter, HTTPException, Depends
from app.models.cases import CaseRequest, Case
from datetime import datetime
from sqlmodel import Session, select
from app.db import get_session
import random
from app.auth.security import get_current_active_user

router = APIRouter(
    prefix="/cases",
    tags=["cases"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/{case_id}", tags=["cases"])
async def read_case(case_id: str, session: Session = Depends(get_session)):
    case = session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.get("/", tags=["cases"])
async def read_all_cases(session: Session = Depends(get_session)):
    cases = session.exec(select(Case)).all()
    return cases


def generate_id():
    return str(random.randint(1, 100000))


@router.post("/", tags=["cases"], response_model=Case)
def create_case(request: CaseRequest, session: Session = Depends(get_session)):
    case = Case(
        category=request.category,
        time=datetime.now(),
        name=request.name,
        id=generate_id(),
    )
    session.add(case)
    session.commit()
    session.refresh(case)
    return case
