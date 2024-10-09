from app.models.base import TableModelMixin
from sqlmodel import Field
from uuid import UUID
from enum import Enum


class EventType(str, Enum):
    case_created = "Case Created"
    case_updated = "Update"
    case_deleted = "Delete"
    login = "Login"
    logout = "Logout"
    error = "Error"
    other = "Other"


class AuditLogEvent(TableModelMixin, table=True):
    __tablename__ = "audit_log"

    event_type: EventType

    # Log events can be associated with a user, but this is not required.
    username: str | None = Field(foreign_key="users.username")

    # Log events can be associated with a case, but this is not required.
    case_id: UUID | None = Field(foreign_key="cases.id", index=True)
