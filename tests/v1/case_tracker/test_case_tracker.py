from app.models.case_tracker import CaseTracker
from app.models.cases import Case, CaseTypes
import uuid
from sqlmodel import Session, select


def create_case_tracker(case_id=None):
    return CaseTracker(
        case_id=case_id or uuid.uuid4(),
        gtm_anon_id=str(uuid.uuid4()),
        journey={
            "source": "access",
            "scope": "access",
            "means": "chs",
            "last_app": "ccq",
        },
    )


def test_create_case_tracker(session: Session):
    case_tracker = create_case_tracker()
    session.add(case_tracker)
    session.commit()
    assert session.exec(select(CaseTracker)).all() == [case_tracker]


def test_case_tracker_journey_dict(session: Session):
    case_tracker = create_case_tracker()
    session.add(case_tracker)
    session.commit()
    expected_journey = case_tracker.journey

    case_tracker = session.exec(select(CaseTracker)).first()
    assert type(case_tracker.journey) is dict
    assert case_tracker.journey == expected_journey


def test_cascade_delete(session: Session):
    """If a case is deleted the case_tracker attached to said case should also be deleted."""
    case = Case(case_type=CaseTypes.CLA)
    case_tracker = create_case_tracker(case_id=case.id)
    session.add(case)
    session.add(case_tracker)
    session.commit()
    assert session.exec(select(CaseTracker)).all() == [case_tracker]

    session.delete(case)
    session.commit()
    assert session.exec(select(CaseTracker)).all() == []
