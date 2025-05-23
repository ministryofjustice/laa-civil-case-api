from typing import List

from fastapi.testclient import TestClient
from sqlmodel import Session
from app.auth.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    authenticate_user,
    token_decode,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from freezegun import freeze_time
import pytest
from jwt import ExpiredSignatureError
from datetime import timedelta, datetime
from app.models.users import User, UserScopes


def test_auth_fail_case(client: TestClient):
    response = client.post(
        "latest/cases/", json={"category": "Housing", "name": "John Doe"}
    )
    json = response.json()
    assert json["detail"] == "Not authenticated"
    assert response.status_code == 401


def test_create_case_disabled_user(client: TestClient, auth_token_disabled_user):
    response = client.get(
        "latest/cases/", headers={"Authorization": f"Bearer {auth_token_disabled_user}"}
    )
    json = response.json()
    assert json["detail"] == "User Disabled"
    assert response.status_code == 401


def test_username_token_fail(client: TestClient):
    response = client.post(
        "latest/token",
        data={"username": "fake_user", "password": "incorrect"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    json = response.json()
    assert json["detail"] == "Incorrect username or password"
    assert response.status_code == 401


def test_raw_token_fail(client: TestClient):
    response = client.post(
        "latest/token",
        data={"username": "cla_admin", "password": "cla_admin"},
        headers={"Content-Type": "raw"},
    )
    assert response.status_code == 422


def test_credential_exception(client: TestClient, auth_token):
    response = client.get(
        "latest/cases/", headers={"Authorization": f"Bearer {auth_token} + 1"}
    )
    json = response.json()
    assert json["detail"] == "Could not validate credentials"
    assert response.status_code == 401


def test_credential_exception_no_user(session, client: TestClient, auth_token):
    username = "cla_admin"
    user = session.get(User, username)
    session.delete(user)
    session.commit()
    response = client.get(
        "latest/cases/", headers={"Authorization": f"Bearer {auth_token}"}
    )
    json = response.json()
    assert json["detail"] == "Could not validate credentials"
    assert response.status_code == 401


def test_authenticate_user(session):
    auth_user = authenticate_user(
        session=session, username="cla_admin", password="incorrect"
    )
    assert not auth_user


def test_password_hashing():
    hashed_password = "password"
    assert verify_password("password", get_password_hash(hashed_password))


def test_create_token():
    token = create_access_token(
        data={"sub": "cla_admin"}, expires_delta=timedelta(minutes=30), scopes=[]
    )
    expected_keys = ["sub", "scopes", "exp"]
    token_data = token_decode(token)
    assert list(token_data.keys()) == expected_keys


def test_token_with_no_expire():
    with freeze_time("2024-08-23 10:00:00"):
        token = create_access_token(data={"sub": "cla_admin"})
        new_time = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES + 10)
    assert token is not None

    with freeze_time(new_time):
        assert pytest.raises(ExpiredSignatureError)


def test_token_defined_expiry():
    with freeze_time("2024-08-23 10:00:00"):
        token = create_access_token(
            data={"sub": "cla_admin"},
            expires_delta=timedelta(minutes=1),
        )
    assert token is not None

    with freeze_time("2024-08-23 10:05:00"):
        assert pytest.raises(ExpiredSignatureError)


def test_scopes_missing_scopes(client: TestClient, session: Session):
    # Create the test user with no given scopes
    # They should not be able to access the GET /cases resource as that requires the  UserScopes.READ scope
    assert_user_scope(session, client, [], "latest/cases", 401)


def test_scopes_incorrect_scope(client: TestClient, session: Session):
    # Create the test user with a UserScopes.CREATE scope
    # They should not be able to access the GET /cases resource as that requires the  UserScopes.READ scope
    assert_user_scope(session, client, [UserScopes.CREATE], "latest/cases", 401)


def test_scopes_correct_scope(client: TestClient, session: Session):
    # Create the test user with a UserScopes.READ scope
    # They should be able to access the GET /cases resource as that requires the  UserScopes.READ scope
    assert_user_scope(session, client, [UserScopes.READ], "latest/cases", 200)


def assert_user_scope(
    session: Session,
    client: TestClient,
    scopes: List[UserScopes],
    resource: str,
    expected_status_code,
):
    # Create the test user with given scopes
    username = "test_assert_user_scope"
    password = "<PASSWORD>"
    user = User(
        username=username, hashed_password=get_password_hash(password), scopes=scopes
    )
    session.add(user)
    session.commit()

    # Obtain an access token for the test user
    response = client.post(
        "latest/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = response.json()["access_token"]
    token_data = token_decode(token)
    assert token_data["scopes"] == scopes

    # Attempt to access a resource with the test user
    client.headers["Authorization"] = f"Bearer {token}"
    response = client.get(resource)
    assert response.status_code == expected_status_code
