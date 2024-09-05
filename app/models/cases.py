from sqlmodel import Field, SQLModel
from app.models.base import TableModelMixin
from app.models.case_types import CaseTypes


class BaseCase(SQLModel):
    case_type: CaseTypes = Field(
        index=True
    )  # Which service is the case originally from
    assigned_to: str | None = Field(
        default=None
    )  # The ID of the user this case is currently assigned to.


class Case(BaseCase, TableModelMixin, table=True):
    __tablename__ = "cases"


class CaseRequest(BaseCase):
    """Request model used to create a new case"""

    pass
