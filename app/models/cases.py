from sqlmodel import Field, Relationship
from typing import List
from app.models.base import TableModelMixin, BaseRequest
from app.models.types.case_types import CaseTypes
from app.models.case_notes import CaseNote, CaseNotesRequest
from app.models.person import Person
from app.models.case_tracker import CaseTracker
from app.models.eligibility_outcomes import EligibilityOutcomes


class Case(TableModelMixin, table=True):
    case_type: CaseTypes = Field(index=True)
    # Cascade delete ensures all related fields are deleted when the attached case is deleted.
    notes: List[CaseNote] = Relationship(back_populates="case", cascade_delete=True)
    people: List[Person] = Relationship(back_populates="case", cascade_delete=True)
    case_tracker: CaseTracker = Relationship(back_populates="case", cascade_delete=True)
    eligibility_outcomes: List[EligibilityOutcomes] = Relationship(
        back_populates="case", cascade_delete=True
    )


class CaseRequest(BaseRequest):
    case_type: CaseTypes
    notes: List[CaseNotesRequest] | None
    # people: List[Person] | None
    # case_tracker: CaseTracker | None
    # eligibility_outcomes: List[EligibilityOutcomes] | None

    class Meta:
        foreign_fields = ["notes"]
        model = Case
