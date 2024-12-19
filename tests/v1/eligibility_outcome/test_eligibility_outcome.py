from app.models.eligibility_outcomes import (
    EligibilityOutcomes,
    EligibilityType,
    EligibilityOutcomeType,
)
from app.models.cases import Case, CaseTypes
import uuid
from sqlmodel import Session, select


def create_eligibility_outcome(case_id=None):
    return EligibilityOutcomes(
        case_id=case_id or uuid.uuid4(),
        eligibility_type=EligibilityType.CFE,
        outcome=EligibilityOutcomeType.INSCOPE,
        answers={"category": "family", "income": {"value": 1000}},
    )


def test_create_eligibility_outcome(session: Session):
    eligibility = create_eligibility_outcome()
    session.add(eligibility)
    session.commit()
    assert session.exec(select(EligibilityOutcomes)).all() == [eligibility]


def test_eligibility_outcome_answers_dict(session: Session):
    eligibility = create_eligibility_outcome()
    session.add(eligibility)
    session.commit()
    expected_answers = eligibility.answers

    eligibility = session.exec(select(EligibilityOutcomes)).first()
    assert type(eligibility.answers) is dict
    assert eligibility.answers == expected_answers


def test_cascade_delete(session: Session):
    """If a case is deleted the eligibility_outcome attached to said case should also be deleted."""
    case = Case(case_type=CaseTypes.CLA)
    eligibility = create_eligibility_outcome(case_id=case.id)
    session.add(case)
    session.add(eligibility)
    session.commit()
    assert session.exec(select(EligibilityOutcomes)).all() == [eligibility]

    session.delete(case)
    session.commit()
    assert session.exec(select(EligibilityOutcomes)).all() == []


def test_cascade_delete_multiple_eligibility_outcomes(session: Session):
    case = Case(case_type=CaseTypes.CLA)
    eligibility_outcomes = [create_eligibility_outcome(case.id) for i in range(5)]
    session.add(case)
    session.add_all(eligibility_outcomes)
    session.commit()
    assert len(session.exec(select(EligibilityOutcomes)).all()) == 5

    session.delete(case)
    session.commit()
    assert len(session.exec(select(EligibilityOutcomes)).all()) == 0
