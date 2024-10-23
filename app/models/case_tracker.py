from uuid import UUID
from sqlmodel import Field, JSON, Relationship
from app.models.base import TableModelMixin, BaseRequest, BaseResponse


class CaseTrackerBase:
    gtm_anon_id: str = Field()
    journey: dict = Field(sa_type=JSON)


class CaseTracker(CaseTrackerBase, TableModelMixin, table=True):
    __tablename__ = "case_tracker"
    case_id: UUID = Field(foreign_key="cases.id", index=True)
    # This allows for linking the case tracker back to the case, this allows us to address case tracker
    # directly by using the `Case.case_tracker` syntax, rather than searching for each eligibility outcome
    # using its ID.
    case: "Case" = Relationship(back_populates="case_tracker")  # noqa: F821


class CaseTrackerRequest(CaseTrackerBase, BaseRequest):
    class Meta:
        model = CaseTracker


class CaseTrackerResponse(CaseTrackerBase, BaseResponse):
    pass
