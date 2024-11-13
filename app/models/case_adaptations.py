from uuid import UUID
from typing import List
from sqlmodel import Field, JSON, Relationship
from app.models.base import (
    TableModelMixin,
    BaseRequest,
    BaseResponse,
    BaseUpdateRequest,
)
from app.models.types.languages import Languages
from app.models.types.adaptations import Adaptations


class CaseAdaptationsBase:
    needed_adaptations: List[Adaptations] = Field(sa_type=JSON, nullable=True)
    languages: List[Languages] = Field(sa_type=JSON, nullable=True)


class CaseAdaptations(CaseAdaptationsBase, TableModelMixin, table=True):
    __tablename__ = "case_adaptations"
    case_id: UUID = Field(foreign_key="cases.id", index=True)
    # This allows for linking the case adaptations back to the case, this allows us to address case adaptations
    # directly by using the `Case.case_adaptations` syntax
    # using its ID.
    case: "Case" = Relationship(back_populates="case_adaptations")  # noqa: F821


class CaseAdaptationsRequest(CaseAdaptationsBase, BaseRequest):
    class Meta:
        model = CaseAdaptations


class CaseAdaptationsUpdateRequest(CaseAdaptationsBase, BaseUpdateRequest):
    class Meta(BaseRequest.Meta):
        model = CaseAdaptations


class CaseAdaptationsResponse(CaseAdaptationsBase, BaseResponse):
    pass
