from fastapi.testclient import TestClient
from sqlmodel import Session


def test_create_case(client: TestClient, session: Session):
    response = client.post(
            "/cases/", json={"category": "Housing", "name": "John Doe"})
    case = response.json()

    assert response.status_code == 200
    assert case["category"] == "Housing"
    assert case["name"] == "John Doe"
    assert case["id"] is not None


def test_read_case(client: TestClient, session: Session):
    response = client.post(
            "/cases/", json={"category": "Housing", "name": "John Doe"})
    case = response.json()

