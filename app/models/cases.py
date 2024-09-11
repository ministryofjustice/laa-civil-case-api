from sqlmodel import Field, SQLModel
from app.models.base import TableModelMixin
from app.models.case_types import CaseTypes


class BaseCase(SQLModel):
    case_type: CaseTypes = Field(
        index=True
    )  # Which service is the case originally from


class Case(BaseCase, TableModelMixin, table=True):
    pass


class CaseRequest(BaseCase):
    """Request model used to create a new case"""

    pass
