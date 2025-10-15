from app.models.cases import Case
from app.models.case_notes import CaseNote, NoteType
import uuid
from sqlmodel import Session, select
from app.models.types.case_types import CaseTypes
from datetime import datetime, UTC


def test_attach_note(session: Session):
    case = Case(case_type=CaseTypes.CLA)
    provider_note = CaseNote(
        case_id=case.id, content="Hello world", note_type=NoteType.provider
    )
    adaptation_note = CaseNote(
        case_id=case.id, content="Needs BSL", note_type=NoteType.adaptation
    )
    session.add(case)
    session.add(provider_note)
    session.add(adaptation_note)
    session.commit()

    assert len(case.notes) == 2
    assert case.notes[0].content == "Hello world"
    assert provider_note.note_type == "Provider"

    assert case.notes[1].content == "Needs BSL"
    assert adaptation_note.note_type == "Adaptation"


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


def test_cascade_delete(session: Session):
    """If a case is deleted all notes attached to said case should also be deleted."""
    case = Case(case_type=CaseTypes.CLA)
    note = CaseNote(case_id=case.id)

    session.add(case)
    session.add(note)
    session.commit()
    session.delete(case)

    # The note will still exist until the delete request has been sent to the database
    assert session.exec(select(CaseNote)).all() == [note]
    session.commit()

    # After the case is deleted the attached note is also removed
    assert session.exec(select(CaseNote)).all() == []


def test_cascade_delete_multiple_notes(session: Session):
    case = Case(case_type=CaseTypes.CLA)
    notes = []
    for i in range(5):
        notes.append(CaseNote(case_id=case.id, content=f"Note: {i}"))

    session.add(case)
    session.add_all(notes)
    session.commit()
    session.delete(case)

    # The notes will still exist until the delete request has been sent to the database
    assert len(session.exec(select(CaseNote)).all()) == 5
    session.commit()

    # After the case is deleted the attached notes are also removed
    assert len(session.exec(select(CaseNote)).all()) == 0


def test_reverse_cascade_delete(session: Session):
    """If a note is deleted we want to make sure the attached case is not deleted."""
    case = Case(case_type=CaseTypes.CLA)
    note = CaseNote(case_id=case.id)
    session.add(case)
    session.add(note)
    session.commit()
    session.delete(note)
    session.commit()
    assert session.exec(select(Case)).all() == [case]
    assert session.exec(select(CaseNote)).all() == []


def test_case_notes_string_format():
    provider_note = CaseNote(note_type=NoteType.provider, case_id=uuid.uuid4())
    assert "Provider note" in str(provider_note)

    operator_note = CaseNote(note_type=NoteType.operator, case_id=uuid.uuid4())
    assert "Operator note" in str(operator_note)

    case_id = uuid.uuid4()
    note = CaseNote(case_id=case_id)
    assert f"Attached to case ID: {case_id}" in str(note)
