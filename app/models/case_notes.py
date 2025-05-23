from sqlmodel import Field, Relationship
from app.models.base import (
    TableModelMixin,
    BaseRequest,
    BaseUpdateRequest,
    BaseResponse,
)
from enum import Enum
from uuid import UUID


class NoteType(str, Enum):
    adaptation = "Adaptation"
    personal = "Personal"
    provider = "Provider"
    caseworker = "Caseworker"
    operator = "Operator"
    other = "Other"


class BaseCaseNote:
    note_type: NoteType = Field(index=True, default=NoteType.other)
    content: str = Field(default="")


class CaseNote(BaseCaseNote, TableModelMixin, table=True):
    __tablename__ = "case_notes"
    case_id: UUID = Field(foreign_key="cases.id")
    # This allows for linking the notes back to the case, this allows us to address case notes directly by using
    # the `Case.notes` syntax, rather than searching for each note using its ID.
    case: "Case" = Relationship(back_populates="notes")  # noqa: F821

    def __str__(self):
        return (
            f"{self.note_type.value} note\n"
            f"Attached to case ID: {self.case_id}"
            f"{self.content}"
        )


class CaseNotesRequest(BaseCaseNote, BaseRequest):
    class Meta(BaseRequest.Meta):
        model = CaseNote


class CaseNotesUpdateRequest(BaseCaseNote, BaseUpdateRequest):
    class Meta(BaseRequest.Meta):
        model = CaseNote


class CaseNotesResponse(BaseCaseNote, BaseResponse):
    pass
