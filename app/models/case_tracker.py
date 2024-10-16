from uuid import UUID
from sqlmodel import SQLModel, Field, JSON, Relationship
from app.models.base import TableModelMixin


class CaseTrackerBase(SQLModel):
    case_id: UUID = Field(foreign_key="cases.id", index=True)
    gtm_anon_id: str = Field()
    journey: dict = Field(sa_type=JSON)


class CaseTracker(CaseTrackerBase, TableModelMixin, table=True):
    __tablename__ = "case_tracker"
    # This allows for linking the case tracker back to the case, this allows us to address case tracker
    # directly by using the `Case.case_tracker` syntax, rather than searching for each eligibility outcome
    # using its ID.
    case: "Case" = Relationship(back_populates="case_tracker")  # noqa: F821
