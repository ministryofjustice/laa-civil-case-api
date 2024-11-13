from sqlmodel import Field, Relationship, Session, SQLModel
from typing import List
from app.models.base import TableModelMixin, BaseRequest, BaseResponse, uuid
from app.models.types.case_types import CaseTypes
from app.models.case_notes import (
    CaseNote,
    CaseNotesRequest,
    CaseNotesResponse,
    CaseNotesUpdateRequest,
)
from app.models.person import Person, PersonRequest, PersonResponse, PersonUpdateRequest
from app.models.case_tracker import (
    CaseTracker,
    CaseTrackerRequest,
    CaseTrackerResponse,
    CaseTrackerUpdateRequest,
)
from app.models.eligibility_outcomes import (
    EligibilityOutcomes,
    EligibilityOutcomesRequest,
    EligibilityOutcomesResponse,
    EligibilityOutcomesUpdateRequest,
)


class BaseCase:
    case_type: CaseTypes = Field(index=True)

    def retrieve(self, session: Session, instance_id: uuid.UUID) -> SQLModel | None:
        return session.get(self.model, instance_id)


class Case(BaseCase, TableModelMixin, table=True):
    case_type: CaseTypes = Field(index=True)
    # Cascade delete ensures all related fields are deleted when the attached case is deleted.
    notes: List[CaseNote] = Relationship(back_populates="case", cascade_delete=True)
    people: List[Person] = Relationship(back_populates="case", cascade_delete=True)
    case_tracker: CaseTracker = Relationship(back_populates="case", cascade_delete=True)
    eligibility_outcomes: List[EligibilityOutcomes] = Relationship(
        back_populates="case", cascade_delete=True
    )


class CaseRetrieve(BaseCase, TableModelMixin):
    case_type: CaseTypes
    # Cascade delete ensures all related fields are deleted when the attached case is deleted.
    notes: List[CaseNote]
    people: List[Person]
    case_tracker: CaseTracker
    eligibility_outcomes: List[EligibilityOutcomes]


class CaseRequest(BaseRequest):
    case_type: CaseTypes
    # These fields all are optional for case create/update requests
    notes: List[CaseNotesRequest] | None = None
    people: List[PersonRequest] | None = None
    case_tracker: CaseTrackerRequest | None = None
    eligibility_outcomes: List[EligibilityOutcomesRequest] | None = None

    class Meta(BaseRequest.Meta):
        model = Case


class CaseUpdateRequest(CaseRequest):
    notes: List[CaseNotesUpdateRequest] | None = None
    people: List[PersonUpdateRequest] | None = None
    case_tracker: CaseTrackerUpdateRequest | None = None
    eligibility_outcomes: List[EligibilityOutcomesUpdateRequest] | None = None


class CaseResponse(BaseCase, BaseResponse):
    notes: List[CaseNotesResponse] | None
    people: List[PersonResponse] | None
    case_tracker: CaseTrackerResponse | None
    eligibility_outcomes: List[EligibilityOutcomesResponse] | None
