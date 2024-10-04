from app.models.cases import Case
from app.models.person import Person
import uuid
from sqlmodel import Session, select
from app.models.types.case_types import CaseTypes


def test_create_person(session: Session):
    person = Person(
        name="John",
        case_id=uuid.uuid4(),
        address="212B Baker Street",
        postcode="EN1 3JY",
        phone_number="01234 56789",
    )
    session.add(person)
    session.commit()
    assert session.exec(select(Person)).all() == [person]


def test_attach_person(session: Session):
    case = Case(case_type=CaseTypes.CLA)
    person = Person(name="Bob", case_id=case.id)
    session.add(case)
    session.add(person)
    session.commit()
    assert len(case.people) == 1
    assert case.people[0].name == "Bob"


def test_cascade_delete(session: Session):
    """If a case is deleted all people attached to said case should also be deleted."""
    case = Case(case_type=CaseTypes.CLA)
    person = Person(case_id=case.id, name="Jane")

    session.add(case)
    session.add(person)
    session.commit()
    session.delete(case)

    # The note will still exist until the delete request has been sent to the database
    assert session.exec(select(Person)).all() == [person]
    session.commit()

    # After the case is deleted the attached note is also removed
    assert session.exec(select(Person)).all() == []


def test_reverse_cascade_delete(session: Session):
    """If a person is deleted we want to make sure the attached case is not deleted."""
    case = Case(case_type=CaseTypes.CLA)
    person = Person(case_id=case.id, name="Lisa")
    session.add(case)
    session.add(person)
    session.commit()
    session.delete(person)
    session.commit()
    assert session.exec(select(Case)).all() == [case]
    assert session.exec(select(Person)).all() == []
