import pytest
from sqlmodel import SQLModel, create_engine, Session, StaticPool
from app import case_api
from app.auth.security import get_current_user
from app.db import get_session
from fastapi.testclient import TestClient

from app.models import Users

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    def override_get_current_user():
        # Return a dummy user or None to bypass authentication
        return Users(username="testuser", hashed_password="dummyhash")

    case_api.dependency_overrides[get_session] = get_session_override

    case_api.dependency_overrides[get_current_user] = override_get_current_user

    client = TestClient(case_api)
    yield client
    case_api.dependency_overrides.clear()
