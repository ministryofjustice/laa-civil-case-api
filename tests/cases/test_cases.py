from fastapi.testclient import TestClient


def test_create_case(client: TestClient):
    response = client.post("/cases/", json={"category": "Housing", "name": "John Doe"})
    case = response.json()

    assert response.status_code == 200
    assert case["category"] == "Housing"
    assert case["name"] == "John Doe"
    assert case["id"] is not None
