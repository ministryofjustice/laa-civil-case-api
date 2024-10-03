from sqlmodel import Field, SQLModel, Relationship
from typing import List
from app.models.base import TableModelMixin
from app.models.case_types import CaseTypes
from app.models.case_notes import CaseNote


class BaseCase(SQLModel):
    case_type: CaseTypes = Field(
        index=True
    )  # Which service is the case originally from


class Case(BaseCase, TableModelMixin, table=True):
    # Cascade delete ensures all related notes are deleted when the attached case is deleted.
    notes: List[CaseNote] = Relationship(back_populates="case", cascade_delete=True)


class CaseRequest(BaseCase):
    """Request model used to create a new case"""

    pass
