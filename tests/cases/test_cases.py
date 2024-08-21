from fastapi.testclient import TestClient

def test_create_case(client: TestClient, auth_token):
    response = client.post(
            "/cases/", json={"category": "Housing", "name": "John Doe"}, headers={"Authorization": f"Bearer {auth_token}"})
    case = response.json()

    assert response.status_code == 200
    assert case["category"] == "Housing"
    assert case["name"] == "John Doe"
    assert case["id"] is not None

def test_create_case_unauthorised(client: TestClient):
    response = client.post(
            "/cases/", json={"category": "Housing", "name": "John Doe"})

    assert response.status_code == 401