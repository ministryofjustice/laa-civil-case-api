from fastapi.testclient import TestClient
import pytest

@pytest.fixture
def auth_token(client):
    # Send POST request with x-www-form-urlencoded data
    response = client.post(
        "/token",
        data={"username": "johndoe", "password": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    return token_data["access_token"]

def test_auth_fail_case(client: TestClient):
    response = client.post(
            "/cases/", json={"category": "Housing", "name": "John Doe"})

    assert response.status_code == 401

