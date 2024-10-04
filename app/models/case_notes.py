from sqlmodel import Field, SQLModel, Relationship
from app.models.base import TableModelMixin
from enum import Enum
from uuid import UUID


class NoteType(str, Enum):
    personal = "Personal"
    provider = "Provider"
    caseworker = "Caseworker"
    operator = "Operator"
    other = "Other"


class BaseCaseNote(SQLModel):
    note_type: NoteType = Field(index=True, default=NoteType.other)
    content: str = Field(default="")
    case_id: UUID = Field(foreign_key="cases.id")


class CaseNote(BaseCaseNote, TableModelMixin, table=True):
    __tablename__ = "case_notes"

    # This allows for linking the notes back to the case, this allows us to address case notes directly by using
    # the `Case.notes` syntax, rather than searching for each note using its ID.
    case: "Case" = Relationship(back_populates="notes")  # noqa: F821

    def __str__(self):
        return (
            f"{self.note_type.value} note\n"
            f"Attached to case ID: {self.case_id}"
            f"{self.content}"
        )
