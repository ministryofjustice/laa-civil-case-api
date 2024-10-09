from app.models.audit_log import AuditLogEvent, EventType
from app.models.users import User
from app.models.cases import Case
from app.models.types.case_types import CaseTypes
from sqlmodel import Session, select


def test_create_user_audit_log_event(session: Session):
    user = session.exec(select(User)).all()[0]
    event = AuditLogEvent(event_type=EventType.login, username=user.username)
    session.add(user)
    session.add(event)
    session.commit()
    statement = select(AuditLogEvent).where(AuditLogEvent.username == user.username)
    events = session.exec(statement).all()
    assert len(events) == 1
    assert events[0].event_type == EventType.login


def test_create_case_audit_log_event(session: Session):
    case = Case(case_type=CaseTypes.CLA)
    event = AuditLogEvent(event_type=EventType.case_created, case_id=case.id)
    session.add(case)
    session.add(event)
    session.commit()
    statement = select(AuditLogEvent).where(AuditLogEvent.case_id == case.id)
    events = session.exec(statement).all()
    assert len(events) == 1
    assert events[0].event_type == EventType.case_created
