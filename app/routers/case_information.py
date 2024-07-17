from fastapi import APIRouter
from ..models.cases import CaseCreate, Case
from datetime import datetime
from sqlmodel import Session
from app.db.database import engine

router = APIRouter(
    prefix="/cases",
    tags=["cases"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{case_id}", tags=["cases"])
async def read_case():
    return [{"case object"}]


def generate_id():
    return "1"

@router.post("/", tags=["cases"], response_model=Case)
def create_case(request: CaseCreate):
    with Session(engine) as session:
        case = Case(category = request.category, time=datetime.now(), name=request.name)
        session.add(case)
        session.commit()
        session.refresh(case)
        return case