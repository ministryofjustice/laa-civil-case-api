from fastapi.testclient import TestClient


def test_auth_fail_case(client: TestClient):
    response = client.post(
            "/cases/", json={"category": "Housing", "name": "John Doe"})

    assert response.status_code == 401

