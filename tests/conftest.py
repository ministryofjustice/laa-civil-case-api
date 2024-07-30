import pytest
from sqlmodel import SQLModel, create_engine, Session, StaticPool
from app import case_api
from app.db import get_session
from fastapi.testclient import TestClient


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

    case_api.dependency_overrides[get_session] = get_session_override

    client = TestClient(case_api)
    yield client
    case_api.dependency_overrides.clear()
