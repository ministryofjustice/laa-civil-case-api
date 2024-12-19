import time
import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.cases import Case
from tests.v1.cases.utils import (
    assert_dicts_equal,
    get_case_test_data,
    create_test_case,
    remove_auto_generated_fields,
)


def test_case_create_request(client_authed: TestClient, session: Session):
    test_data = get_case_test_data()
    response_json = client_authed.post("v1/cases", json=test_data).json()
    assert_dicts_equal(response_json, test_data)


def test_case_create_request_minimal(client_authed: TestClient, session: Session):
    """Test the minimum data required to create a case."""
    test_data = {"case_type": "Check if your client qualifies for legal aid"}
    response_json = client_authed.post("v1/cases", json=test_data).json()

    expected_data = {
        **test_data,
        **{
            "notes": [],
            "people": [],
            "case_tracker": None,
            "eligibility_outcomes": [],
            "case_adaptations": None,
        },
    }
    assert_dicts_equal(response_json, expected_data)


def test_case_create_request_not_enough_data(
    client_authed: TestClient, session: Session
):
    """Test that we cannot create a without providing the minimum data required."""
    test_data = {}
    response = client_authed.post("v1/cases", json=test_data)
    assert response.status_code == 422
    assert response.reason_phrase == "Unprocessable Entity"


def test_case_update_request(client_authed: TestClient, session: Session):
    """Test we can update a case"""
    original_case = create_test_case(session)
    test_data = {
        "case_type": "Civil Legal Advice",
        "notes": [],
        "people": [
            {
                "name": "John Doe",
                "address": "102 Petty France",
                "phone_number": "11111111",
                "postcode": "SW1 1AA",
                "email": "user1@example.com",
            },
            {
                "name": "Jane Doe",
                "address": "10SC Canary Wharf",
                "phone_number": "222222222",
                "postcode": "SW2 2AA",
                "email": "user2@example.com",
            },
        ],
    }

    response = client_authed.put(f"v1/cases/{original_case.id}", json=test_data)
    updated_case = session.get(Case, original_case.id)
    assert response.status_code == 200
    assert updated_case.case_type == "Civil Legal Advice"
    assert updated_case.notes == []
    assert len(updated_case.people) == 2
    for index, person in enumerate(updated_case.people):
        actual = remove_auto_generated_fields(person.model_dump())
        expected = test_data["people"][index]
        assert actual == expected, "Expected people did not match"

    # We did not send a payload for this field so it should remain unchanged
    assert updated_case.case_tracker.gtm_anon_id == "string"

    # We did not send a payload for this field so it should remain unchanged
    assert len(updated_case.eligibility_outcomes) == 1
    for index, eligibility_outcome in enumerate(updated_case.eligibility_outcomes):
        actual = remove_auto_generated_fields(eligibility_outcome.model_dump())
        expected = remove_auto_generated_fields(
            original_case.eligibility_outcomes[index].model_dump()
        )
        assert actual == expected, "Expected eligibility_outcomes did not match"


def test_case_update_existing_request(client_authed: TestClient, session: Session):
    """Test we can update a case with an existing person"""
    original_case = create_test_case(session)
    original_created_at = original_case.people[0].created_at
    original_updated_at = original_case.people[0].updated_at
    time.sleep(0.25)
    test_data = {
        "case_type": "Civil Legal Advice",
        "people": [
            {
                "id": str(original_case.people[0].id),
                "name": "John Doe",
                "address": "102 Petty France",
                "phone_number": "11111111",
                "postcode": "SW1 1AA",
                "email": "user1@example.com",
            },
        ],
    }

    response = client_authed.put(f"v1/cases/{original_case.id}", json=test_data)
    updated_case = session.get(Case, original_case.id)
    assert response.status_code == 200
    assert updated_case.people[0].updated_at > original_updated_at
    assert updated_case.people[0].created_at == original_created_at


def test_case_update_invalid_id_request(client_authed: TestClient, session: Session):
    """Test that updating a nested relationship with an invalid id results in an error."""
    case = create_test_case(session)
    test_data = {
        "case_type": "Civil Legal Advice",
        "people": [
            {
                "id": str(uuid.uuid4()),
                "name": "John Doe",
                "address": "102 Petty France",
                "phone_number": "11111111",
                "postcode": "SW1 1AA",
                "email": "user1@example.com",
            },
        ],
    }

    response = client_authed.put(f"v1/cases/{case.id}", json=test_data)
    assert response.status_code == 404
