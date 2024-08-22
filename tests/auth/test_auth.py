from fastapi.testclient import TestClient
from app.auth.security import *

def test_auth_fail_case(client: TestClient):
    response = client.post(
            "/cases/", json={"category": "Housing", "name": "John Doe"})

    assert response.status_code == 401

def test_username_token_fail(client):
    response = client.post(
        "/token",
        data={"username": "cla_admin", "password": "incorrect"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401

def test_raw_token_fail(client):
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
