from uuid import UUID
from enum import Enum
from sqlmodel import Field, JSON, Relationship
from app.models.base import TableModelMixin, BaseRequest, BaseResponse


class EligibilityType(str, Enum):
    CCQ = "CCQ"
    MEANS = "MEANS"
    CFE = "CFE"


class EligibilityOutcomeType(str, Enum):
    INSCOPE = "In scope"
    OUTOFSCOPE = "Out of scope"
    UNKNOWN = "Unknown"


class EligibilityOutcomesBase:
    eligibility_type: EligibilityType = Field(index=True)
    outcome: EligibilityOutcomeType = Field(index=True)
    answers: dict = Field(sa_type=JSON)


class EligibilityOutcomes(EligibilityOutcomesBase, TableModelMixin, table=True):
    __tablename__ = "eligibility_outcomes"
    case_id: UUID = Field(foreign_key="cases.id", index=True)
    # This allows for linking the eligibility outcome back to the case, this allows us to address eligibility outcome
    # directly by using the `Case.eligibility_outcome` syntax, rather than searching for each eligibility outcome
    # using its ID.
    case: "Case" = Relationship(back_populates="eligibility_outcomes")  # noqa: F821


class EligibilityOutcomesRequest(EligibilityOutcomesBase, BaseRequest):
    class Meta:
        model = EligibilityOutcomes


class EligibilityOutcomesResponse(EligibilityOutcomesBase, BaseResponse):
    pass
