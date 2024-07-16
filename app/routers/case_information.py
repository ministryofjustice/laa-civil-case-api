from fastapi import APIRouter
from ..models.request.cases import Case as RequestCase
from app.models.db.cases import Cases
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

@router.post("/", tags=["cases"], response_model=Cases)
def create_case(request: RequestCase):
    with Session(engine) as session:
        case = Cases(category = request.category, id="a", time=datetime.now())
        session.add(case)
        session.commit()
        session.refresh(case)
        return case