from fastapi import APIRouter
from ..models.request.cases import Case as RequestCase
from ..models.response.cases import Case as ResponseCase
from datetime import datetime

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

@router.post("/", tags=["cases"], response_model=ResponseCase)
async def create_case(case: RequestCase):
    id =  generate_id()
    return ResponseCase(category=case.category, id=id, time=datetime.now())