import uuid
from freezegun import freeze_time
from unittest.mock import patch
from sqlmodel import Session
from app.models.cases import CaseRequest, Case
from app.models.case_notes import CaseNote
from app.models.person import Person
from app.models.case_tracker import CaseTracker
from app.models.eligibility_outcomes import EligibilityOutcomes

TEST_DATA = {
    "case_type": "Check if your client qualifies for legal aid",
    "notes": [{"note_type": "Other", "content": ""}],
    "people": [
        {
            "name": "string",
            "address": "string",
            "phone_number": "0202 21212",
            "postcode": "sw1 1aa",
            "email": "user@example.com",
        }
    ],
    "case_tracker": {"gtm_anon_id": "string", "journey": {}},
    "eligibility_outcomes": [
        {"eligibility_type": "CCQ", "outcome": "In scope", "answers": {}}
    ],
}


@patch("app.models.base.uuid.uuid4")
@freeze_time("2024-08-23 10:00:00")
def test_case_request(mock_uuid, session: Session):
    mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")

    case_request = CaseRequest(**TEST_DATA)
    data = case_request.translate()
    expected_result = {
        "case_type": "Check if your client qualifies for legal aid",
        "notes": [CaseNote(**TEST_DATA["notes"][0])],
        "people": [Person(**TEST_DATA["people"][0])],
        "case_tracker": CaseTracker(**TEST_DATA["case_tracker"]),
        "eligibility_outcomes": [
            EligibilityOutcomes(**TEST_DATA["eligibility_outcomes"][0])
        ],
    }

    assert data == expected_result
    case = Case(**data)
    session.add(case)
    session.commit()
