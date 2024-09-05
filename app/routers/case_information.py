from typing import Sequence

from fastapi import APIRouter, HTTPException, Depends

from app.models.cases import CaseRequest, Case
from sqlmodel import Session, select
from app.db import get_session
from app.auth.security import get_current_active_user
from uuid import UUID


router = APIRouter(
    prefix="/cases",
    tags=["cases"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/{case_id}", tags=["cases"])
async def read_case(case_id: UUID, session: Session = Depends(get_session)) -> Case:
    case: Case | None = session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.get("/", tags=["cases"])
async def read_all_cases(session: Session = Depends(get_session)) -> Sequence[Case]:
    cases = session.exec(select(Case)).all()
    return cases


@router.post("/", tags=["cases"], response_model=Case)
def create_case(request: CaseRequest, session: Session = Depends(get_session)) -> Case:
    case = Case(**request.dict())
    session.add(case)
    session.commit()
    session.refresh(case)
    return case
