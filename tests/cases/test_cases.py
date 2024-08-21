from fastapi.testclient import TestClient
from tests.auth.test_auth import auth_token

def test_create_case(client: TestClient, auth_token):
    response = client.post(
            "/cases/", json={"category": "Housing", "name": "John Doe"}, headers={"Authorization": f"Bearer {auth_token}"})
    case = response.json()

    assert response.status_code == 200
    assert case["category"] == "Housing"
    assert case["name"] == "John Doe"
    assert case["id"] is not None
