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
    
    case_api.dependency_overrides[get_session] = get_session_override

    client = TestClient(case_api)
    yield client
    case_api.dependency_overrides.clear()

@pytest.fixture()
def auth_token(client):
    # Send POST request with x-www-form-urlencoded data
    response = client.post(
        "/token",  # Adjust this to match your token endpoint
        data={"username": "johndoe", "password": "password"},  # Replace with appropriate credentials
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    return token_data["access_token"]