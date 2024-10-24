from sqlmodel import Field, Relationship
from typing import List
from app.models.base import TableModelMixin, BaseRequest, BaseResponse
from app.models.types.case_types import CaseTypes
from app.models.case_notes import CaseNote, CaseNotesRequest, CaseNotesResponse
from app.models.person import Person, PersonRequest, PersonResponse
from app.models.case_tracker import CaseTracker, CaseTrackerRequest, CaseTrackerResponse
from app.models.eligibility_outcomes import (
    EligibilityOutcomes,
    EligibilityOutcomesRequest,
    EligibilityOutcomesResponse,
)


class BaseCase:
    case_type: CaseTypes = Field(index=True)


class Case(BaseCase, TableModelMixin, table=True):
    # Cascade delete ensures all related fields are deleted when the attached case is deleted.
    notes: List[CaseNote] = Relationship(back_populates="case", cascade_delete=True)
    people: List[Person] = Relationship(back_populates="case", cascade_delete=True)
    case_tracker: CaseTracker = Relationship(back_populates="case", cascade_delete=True)
    eligibility_outcomes: List[EligibilityOutcomes] = Relationship(
        back_populates="case", cascade_delete=True
    )


class CaseRequest(BaseCase, BaseRequest):
    notes: List[CaseNotesRequest] | None = None
    people: List[PersonRequest] | None = None
    case_tracker: CaseTrackerRequest | None = None
    eligibility_outcomes: List[EligibilityOutcomesRequest] | None = None

    class Meta(BaseRequest.Meta):
        model = Case


class CaseResponse(BaseCase, BaseResponse):
    notes: List[CaseNotesResponse] | None
    people: List[PersonResponse] | None
    case_tracker: CaseTrackerResponse | None
    eligibility_outcomes: List[EligibilityOutcomesResponse] | None

    class Config:
        orm_mode = True
