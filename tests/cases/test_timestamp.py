from sqlmodel import Session
from app.models.cases import Case
from app.models.types.case_types import CaseTypes
from datetime import datetime, UTC


def test_timezone():
    case = Case(case_type=CaseTypes.CLA)
    assert case.created_at.tzinfo == UTC


def test_created_at():
    before_case_creation = datetime.now(UTC)
    case = Case(case_type=CaseTypes.CLA)
    after_case_creation = datetime.now(UTC)
    assert before_case_creation < case.created_at < after_case_creation


def test_created_at_read_from_db(session: Session):
    before_creation = datetime.now(UTC)
    original_case = Case(case_type=CaseTypes.CLA)
    session.add(original_case)
    session.commit()
    case = session.get(Case, original_case.id)
    assert before_creation <= case.created_at.replace(tzinfo=UTC) <= datetime.now(UTC)


def test_update_timestamp(session: Session):
    case = Case(case_type=CaseTypes.CLA)
    session.add(case)
    session.commit()

    initial_updated_at = case.updated_at

    case.case_type = CaseTypes.CCQ  # Update the case
    session.add(case)
    session.commit()

    assert case.updated_at > initial_updated_at
