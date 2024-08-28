import pytest
from sqlmodel import SQLModel, create_engine, Session, StaticPool
from app import case_api
from app.db import get_session
from fastapi.testclient import TestClient

from app.auth.security import get_password_hash
from app.models.users import Users

SECRET_KEY = "TEST_KEY"


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    users_to_add = [
        {"username": "cla_admin", "password": "cla_admin", "disabled": False},
        {"username": "jane_doe", "password": "password", "disabled": True},
    ]
    with Session(engine) as session:
        for user in users_to_add:
            username = user.get("username")
            password = user.get("password")
            disabled = user.get("disabled")

            password = get_password_hash(password)
            new_user = Users(
                username=username, hashed_password=password, disabled=disabled
            )
            session.add(new_user)

        session.commit()
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    case_api.dependency_overrides[get_session] = get_session_override

    client = TestClient(case_api)
    yield client
    case_api.dependency_overrides.clear()


@pytest.fixture
def auth_token(client):
    # Send POST request with x-www-form-urlencoded data
    response = client.post(
        "/token",
        data={"username": "cla_admin", "password": "cla_admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    return token_data["access_token"]


@pytest.fixture
def auth_token_disabled_user(client):
    # Send POST request with x-www-form-urlencoded data
    response = client.post(
        "/token",
        data={"username": "jane_doe", "password": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    return token_data["access_token"]
