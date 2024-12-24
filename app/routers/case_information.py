import structlog
from typing import Sequence
from uuid import UUID
from fastapi import APIRouter, HTTPException, Security, Depends
from sqlmodel import Session, select
from app.models.cases import (
    CaseRequest,
    Case,
    CaseResponse,
    CaseUpdateRequest,
)
from app.db import get_session
from app.auth.security import get_current_active_user
from app.models.users import UserScopes

logger = structlog.getLogger(__name__)


router = APIRouter(
    prefix="/cases",
    tags=["cases"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_current_active_user)],
)


@router.get(
    "/{case_id}",
    tags=["cases"],
    response_model=CaseResponse,
    dependencies=[Security(get_current_active_user, scopes=[UserScopes.READ])],
)
async def read_case(case_id: UUID, session: Session = Depends(get_session)) -> Case:
    case: Case | None = session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.get(
    "/",
    tags=["cases"],
    dependencies=[Security(get_current_active_user, scopes=[UserScopes.READ])],
)
async def read_all_cases(session: Session = Depends(get_session)) -> Sequence[Case]:
    cases = session.exec(select(Case)).all()
    return cases


@router.post(
    "/",
    tags=["cases"],
    response_model=CaseResponse,
    status_code=201,
    dependencies=[Security(get_current_active_user, scopes=[UserScopes.CREATE])],
)
def create_case(
    request: CaseRequest,
    session: Session = Depends(get_session),
    user=Depends(get_current_active_user),
):
    case = request.create(session)
    logger.info("Case created", case_id=case.id, user=user.username)
    return case


@router.put(
    "/{case_id}",
    tags=["cases"],
    response_model=CaseResponse,
    dependencies=[Security(get_current_active_user, scopes=[UserScopes.UPDATE])],
)
def update_case(
    case_id: UUID, request: CaseUpdateRequest, session: Session = Depends(get_session)
):
    case = request.retrieve(session, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return request.update(case, session)
