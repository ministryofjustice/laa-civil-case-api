from app.models.cases import Case
from app.models.case_notes import CaseNote, NoteType
import uuid
from sqlmodel import Session
from app.models.case_types import CaseTypes
from datetime import datetime, UTC


def test_attach_note(session: Session):
    case = Case(case_type=CaseTypes.CLA)
    note = CaseNote(case_id=case.id, content="Hello world", note_type=NoteType.provider)
    session.add(case)
    session.add(note)
    session.commit()
    assert len(case.notes) == 1
    assert case.notes[0].content == "Hello world"
    assert note.note_type == "Provider"


def test_empty_note(session: Session):
    case = Case(case_type=CaseTypes.CLA)
    note = CaseNote(case_id=case.id)
    session.add(case)
    session.add(note)
    session.commit()
    assert len(case.notes) == 1
    assert case.notes[0].content == ""


def test_default_note_type():
    assert CaseNote(case_id=uuid.uuid4()).note_type == "Other"


def test_created_at():
    before = datetime.now(UTC)
    note = CaseNote(case_id=uuid.uuid4())
    after = datetime.now(UTC)
    assert before <= note.created_at <= after


def test_updated_at(session: Session):
    note = CaseNote(case_id=uuid.uuid4(), content="Created")
    session.add(note)
    session.commit()
    after_creation = datetime.now(UTC)

    note.content = "Updated"
    session.add(note)
    session.commit()

    assert note.updated_at.replace(tzinfo=UTC) > after_creation
    assert note.content == "Updated"
