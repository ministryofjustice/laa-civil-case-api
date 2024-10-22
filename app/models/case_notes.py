from sqlmodel import Field, Relationship
from app.models.base import TableModelMixin, BaseRequest
from enum import Enum
from uuid import UUID


class NoteType(str, Enum):
    personal = "Personal"
    provider = "Provider"
    caseworker = "Caseworker"
    operator = "Operator"
    other = "Other"


class CaseNote(TableModelMixin, table=True):
    __tablename__ = "case_notes"
    note_type: NoteType = Field(index=True, default=NoteType.other)
    content: str = Field(default="")
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


class CaseNotesRequest(BaseRequest):
    note_type: NoteType
    content: str

    class Meta:
        model = CaseNote
