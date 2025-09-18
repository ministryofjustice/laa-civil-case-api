"""
Standalone tests for client support needs endpoints in mock_data.py.
These tests work independently of the main app to avoid versionizer compatibility issues.
"""

import pytest
from unittest.mock import patch
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

# Import the router and models directly
from app.routers.mock_data import (
    router,
)
from app.models.mock_case import ClientSupportNeedsCreate


# Create a test FastAPI app with just our router
test_app = FastAPI()
test_app.include_router(router)
client = TestClient(test_app)


@pytest.fixture
def mock_data():
    """Sample mock data for testing."""
    return [
        {
            "fullName": "Ember Hamilton",
            "caseReference": "PC-3184-5962",
            "refCode": "",
            "dateReceived": "2025-01-08T19:00:00-05:00",
            "lastModified": "2025-01-09T14:30:00-05:00",
            "caseStatus": "Accepted",
            "dateOfBirth": "1987-02-19T00:00:00-05:00",
            "clientIsVulnerable": True,
            "language": "English",
            "phoneNumber": "0776744581",
            "safeToCall": False,
            "announceCall": True,
            "emailAddress": "ehamilton@yahoo.com",
            "address": "25 Victoria Road, Edinburgh",
            "postcode": "G1 8LB",
            "laaReference": "4235871",
            "thirdParty": {
                "fullName": "Alex Rivers",
                "emailAddress": "alex@rivers.com",
                "contactNumber": "",
                "safeToCall": False,
                "address": "22 Baker Street, London",
                "postcode": "NW1 6XE",
                "relationshipToClient": {
                    "selected": ["Other"],
                },
                "passphraseSetUp": {
                    "selected": ["Yes"],
                    "passphrase": "Secret123",
                },
            },
        },
        {
            "fullName": "Maya Patel",
            "caseReference": "PC-8765-4321",
            "refCode": "",
            "dateReceived": "2025-02-15T19:00:00-05:00",
            "lastModified": "2025-02-16T14:20:00-05:00",
            "caseStatus": "New",
            "dateOfBirth": "1990-05-10T00:00:00-05:00",
            "clientIsVulnerable": False,
            "language": "Hindi",
            "phoneNumber": "0789123456",
            "safeToCall": True,
            "announceCall": False,
            "emailAddress": "maya.patel@example.com",
            "address": "456 Queen Street, Manchester",
            "postcode": "M1 2AB",
            "laaReference": "7891234",
            # No thirdParty or clientSupportNeeds
        },
    ]


class TestClientSupportNeedsEndpoints:
    """Test the client support needs related API endpoints."""

    def test_add_client_support_needs_success(self, mock_data):
        """Test POST /mock/cases/{case_reference}/client-support-needs endpoint with valid data."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file") as mock_save:
                mock_find.return_value = (mock_data[1], 1, mock_data)

                response = client.post(
                    "/mock/cases/PC-8765-4321/client-support-needs",
                    json={
                        "bslWebcam": "No",
                        "textRelay": "No",
                        "callbackPreference": "No",
                        "languageSupportNeeds": "English",
                        "notes": "Here are some notes from the operator",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["caseReference"] == "PC-8765-4321"
        assert data["clientSupportNeeds"]["bslWebcam"] == "No"
        assert data["clientSupportNeeds"]["textRelay"] == "No"
        assert data["clientSupportNeeds"]["callbackPreference"] == "No"
        assert data["clientSupportNeeds"]["languageSupportNeeds"] == "English"
        assert (
            data["clientSupportNeeds"]["notes"]
            == "Here are some notes from the operator"
        )
        mock_save.assert_called_once()

    def test_add_client_support_needs_minimal_data(self, mock_data):
        """Test adding client support needs with only one field."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file"):
                mock_find.return_value = (mock_data[1], 1, mock_data)

                response = client.post(
                    "/mock/cases/PC-8765-4321/client-support-needs",
                    json={"languageSupportNeeds": "British Sign Language"},
                )

        assert response.status_code == 200
        data = response.json()
        assert (
            data["clientSupportNeeds"]["languageSupportNeeds"]
            == "British Sign Language"
        )
        # Other fields should have None values since they weren't provided
        assert data["clientSupportNeeds"]["bslWebcam"] is None
        assert data["clientSupportNeeds"]["textRelay"] is None
        assert data["clientSupportNeeds"]["callbackPreference"] is None
        assert data["clientSupportNeeds"]["notes"] is None

    def test_add_client_support_needs_empty_body(self, mock_data):
        """Test adding client support needs with empty request body."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file"):
                mock_find.return_value = (mock_data[1], 1, mock_data)

                response = client.post(
                    "/mock/cases/PC-8765-4321/client-support-needs",
                    json={},
                )

        assert response.status_code == 200
        data = response.json()
        # Should have clientSupportNeeds object with all None values
        assert data["clientSupportNeeds"]["bslWebcam"] is None
        assert data["clientSupportNeeds"]["textRelay"] is None
        assert data["clientSupportNeeds"]["callbackPreference"] is None
        assert data["clientSupportNeeds"]["languageSupportNeeds"] is None
        assert data["clientSupportNeeds"]["notes"] is None

    def test_add_client_support_needs_case_not_found(self):
        """Test adding client support needs to non-existent case."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            mock_find.side_effect = HTTPException(
                status_code=404, detail="Case with reference 'PC-9999-9999' not found"
            )

            response = client.post(
                "/mock/cases/PC-9999-9999/client-support-needs",
                json={"languageSupportNeeds": "Welsh"},
            )

        assert response.status_code == 404
        assert (
            "Case with reference 'PC-9999-9999' not found" in response.json()["detail"]
        )

    def test_update_client_support_needs_success(self, mock_data):
        """Test PUT /mock/cases/{case_reference}/client-support-needs endpoint with valid data."""
        # Set up a case with existing client support needs
        test_case = mock_data[0].copy()
        test_case["clientSupportNeeds"] = {
            "bslWebcam": "No",
            "textRelay": "No",
            "callbackPreference": "No",
            "languageSupportNeeds": "English",
            "notes": "Original notes",
        }

        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file") as mock_save:
                mock_find.return_value = (test_case, 0, mock_data)

                response = client.put(
                    "/mock/cases/PC-3184-5962/client-support-needs",
                    json={
                        "bslWebcam": "Yes",
                        "languageSupportNeeds": "British Sign Language",
                        "notes": "Updated notes - BSL interpreter required",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["clientSupportNeeds"]["bslWebcam"] == "Yes"
        assert (
            data["clientSupportNeeds"]["languageSupportNeeds"]
            == "British Sign Language"
        )
        assert (
            data["clientSupportNeeds"]["notes"]
            == "Updated notes - BSL interpreter required"
        )
        # Unchanged fields should remain the same
        assert data["clientSupportNeeds"]["textRelay"] == "No"
        assert data["clientSupportNeeds"]["callbackPreference"] == "No"
        mock_save.assert_called_once()

    def test_update_client_support_needs_no_existing_data(self, mock_data):
        """Test updating client support needs when case has no existing data."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            mock_find.return_value = (mock_data[1], 1, mock_data)

            response = client.put(
                "/mock/cases/PC-8765-4321/client-support-needs",
                json={"languageSupportNeeds": "Welsh"},
            )

        assert response.status_code == 404
        assert (
            "No client support needs information found for case"
            in response.json()["detail"]
        )

    def test_delete_client_support_needs_success(self, mock_data):
        """Test DELETE /mock/cases/{case_reference}/client-support-needs when client support needs exists"""
        # Set up a case with existing client support needs
        test_case = mock_data[0].copy()
        test_case["clientSupportNeeds"] = {
            "bslWebcam": "Yes",
            "textRelay": "Yes",
            "languageSupportNeeds": "British Sign Language",
            "notes": "BSL interpreter required",
        }

        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file") as mock_save:
                mock_find.return_value = (test_case, 0, mock_data)

                response = client.delete(
                    "/mock/cases/PC-3184-5962/client-support-needs",
                )

        assert response.status_code == 200
        data = response.json()
        assert data["caseReference"] == "PC-3184-5962"
        assert data["clientSupportNeeds"] is None
        mock_save.assert_called_once()

    def test_delete_client_support_needs_case_not_found(self):
        """Test DELETE /mock/cases/{case_reference}/client-support-needs when case not found"""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            mock_find.side_effect = HTTPException(
                status_code=404, detail="Case with reference 'PC-9999-9999' not found"
            )
            response = client.delete(
                "/mock/cases/PC-9999-9999/client-support-needs",
            )
        assert response.status_code == 404
        assert (
            "Case with reference 'PC-9999-9999' not found" in response.json()["detail"]
        )

    def test_delete_client_support_needs_no_existing_data(self, mock_data):
        """Test DELETE /mock/cases/{case_reference}/client-support-needs when no existing data"""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            mock_find.return_value = (mock_data[1], 1, mock_data)
            response = client.delete("/mock/cases/PC-8765-4321/client-support-needs")
        assert response.status_code == 404
        assert (
            "No client support needs information found for case"
            in response.json()["detail"]
        )


class TestClientSupportNeedsModels:
    """Test ClientSupportNeeds model validation."""

    def test_client_support_needs_create_valid(self):
        """Test creating ClientSupportNeedsCreate with valid data."""
        data = ClientSupportNeedsCreate(
            bslWebcam="Yes",
            textRelay="No",
            callbackPreference="Yes",
            languageSupportNeeds="British Sign Language",
            notes="Client requires BSL interpreter",
        )
        assert data.bslWebcam == "Yes"
        assert data.textRelay == "No"
        assert data.callbackPreference == "Yes"
        assert data.languageSupportNeeds == "British Sign Language"
        assert data.notes == "Client requires BSL interpreter"

    def test_client_support_needs_create_minimal(self):
        """Test creating ClientSupportNeedsCreate with minimal data."""
        data = ClientSupportNeedsCreate(languageSupportNeeds="English")
        assert data.languageSupportNeeds == "English"
        assert data.bslWebcam is None
        assert data.textRelay is None
        assert data.callbackPreference is None
        assert data.notes is None

    def test_client_support_needs_create_empty(self):
        """Test creating ClientSupportNeedsCreate with no data."""
        data = ClientSupportNeedsCreate()
        assert data.bslWebcam is None
        assert data.textRelay is None
        assert data.callbackPreference is None
        assert data.languageSupportNeeds is None
        assert data.notes is None

    def test_client_support_needs_create_all_none(self):
        """Test creating ClientSupportNeedsCreate with all None values."""
        data = ClientSupportNeedsCreate(
            bslWebcam=None,
            textRelay=None,
            callbackPreference=None,
            languageSupportNeeds=None,
            notes=None,
        )
        assert data.bslWebcam is None
        assert data.textRelay is None
        assert data.callbackPreference is None
        assert data.languageSupportNeeds is None
        assert data.notes is None

    def test_client_support_needs_create_string_values(self):
        """Test creating ClientSupportNeedsCreate with various string values."""
        # Test typical "Yes/No" values
        data = ClientSupportNeedsCreate(
            bslWebcam="Yes",
            textRelay="No",
            callbackPreference="Yes",
            languageSupportNeeds="Welsh",
            notes="",
        )
        assert data.bslWebcam == "Yes"
        assert data.textRelay == "No"
        assert data.callbackPreference == "Yes"
        assert data.languageSupportNeeds == "Welsh"
        assert data.notes == ""

    def test_client_support_needs_create_long_strings(self):
        """Test creating ClientSupportNeedsCreate with longer string values."""
        long_notes = "This is a very long note about the client's support needs including specific requirements for BSL interpretation and text relay services during all communications."
        data = ClientSupportNeedsCreate(
            languageSupportNeeds="British Sign Language with certified interpreter",
            notes=long_notes,
        )
        assert (
            data.languageSupportNeeds
            == "British Sign Language with certified interpreter"
        )
        assert data.notes == long_notes

    def test_client_support_needs_create_edge_cases(self):
        """Test creating ClientSupportNeedsCreate with edge case values."""
        data = ClientSupportNeedsCreate(
            bslWebcam="",  # Empty string
            textRelay="Maybe",  # Non-standard value
            callbackPreference="0",  # Number as string
            languageSupportNeeds="Multiple: English, Welsh, BSL",  # Complex value
            notes="   ",  # Whitespace only
        )
        assert data.bslWebcam == ""
        assert data.textRelay == "Maybe"
        assert data.callbackPreference == "0"
        assert data.languageSupportNeeds == "Multiple: English, Welsh, BSL"
        assert data.notes == "   "


if __name__ == "__main__":
    # Run a simple test to verify the setup works
    print("Running basic test...")

    # Test model creation
    model = ClientSupportNeedsCreate(
        bslWebcam="Yes", languageSupportNeeds="English", notes="Test notes"
    )
    print(f"Model created successfully: {model}")

    # Test API endpoint structure (without actual HTTP calls)
    print("API endpoints are defined and ready for testing")
    print("Tests completed successfully!")
