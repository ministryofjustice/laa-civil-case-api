import pytest
from sqlmodel import SQLModel, create_engine, Session, StaticPool
from app import case_api
from app.db import get_session
from app.db.session import CustomSession
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.auth.security import get_password_hash
from app.models.users import User, UserScopes

SECRET_KEY = "TEST_KEY"


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    test_session = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, class_=CustomSession
    )
    SQLModel.metadata.create_all(engine)
    users_to_add = [
        {"username": "cla_admin", "password": "cla_admin", "disabled": False},
        {"username": "jane_doe", "password": "password", "disabled": True},
    ]
    with test_session() as db_session:
        for user in users_to_add:
            username = user.get("username")
            password = user.get("password")
            disabled = user.get("disabled")

            password = get_password_hash(password)
            new_user = User(
                username=username,
                hashed_password=password,
                disabled=disabled,
                scopes=[
                    UserScopes.CREATE,
                    UserScopes.READ,
                    UserScopes.UPDATE,
                    UserScopes.DELETE,
                ],
            )
            db_session.add(new_user)

        db_session.commit()
        yield db_session


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
        "latest/token",
        data={"username": "cla_admin", "password": "cla_admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    return token_data["access_token"]


@pytest.fixture(name="client_authed")
def client_authed(auth_token, client: TestClient, session: Session):
    client.headers["Authorization"] = f"Bearer {auth_token}"
    return client


@pytest.fixture
def auth_token_disabled_user(client):
    # Send POST request with x-www-form-urlencoded data
    response = client.post(
        "latest/token",
        data={"username": "jane_doe", "password": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    return token_data["access_token"]
