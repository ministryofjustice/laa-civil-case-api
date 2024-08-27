from fastapi.testclient import TestClient
from app.auth.security import *

def test_auth_fail_case(client: TestClient):
    response = client.post(
            "/cases/", json={"category": "Housing", "name": "John Doe"})
    json = response.json()
    assert json["detail"] == 'Not authenticated'
    assert response.status_code == 401

def test_create_case_disabled_user(client: TestClient, auth_token_disabled_user):
    response = client.get(
            "/cases/", headers={"Authorization": f"Bearer {auth_token_disabled_user}"})
    json = response.json()
    assert json["detail"] == 'User Disabled'
    assert response.status_code == 401

def test_username_token_fail(client: TestClient):
    response = client.post(
        "/token",
        data={"username": "cla_admin", "password": "incorrect"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    json = response.json()
    assert json["detail"] == 'Incorrect username or password'
    assert response.status_code == 401

def test_raw_token_fail(client: TestClient):
    response = client.post(
        "/token",
        data={"username": "cla_admin", "password": "cla_admin"},
        headers={"Content-Type": "raw"}
    )
    assert response.status_code == 422

def test_password_hashing():
    hashed_password = 'password'
    assert verify_password('password', get_password_hash(hashed_password))

def test_create_token():
    jwt = create_access_token(data={"sub": 'cla_admin'}, expires_delta=timedelta(minutes=30))
    assert len(jwt) == 129
    
