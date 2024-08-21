from fastapi.testclient import TestClient


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